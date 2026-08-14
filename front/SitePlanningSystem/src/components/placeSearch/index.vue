<template>
  <div ref="rootRef" class="place-search" :class="{ 'is-open': panelOpen }" @mousedown.stop>
    <div class="place-search__field">
      <span class="place-search__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="6.2" fill="none" stroke="currentColor" stroke-width="1.7" />
          <path d="M15.8 15.8 20 20" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" />
        </svg>
      </span>
      <input
        ref="inputRef"
        v-model="query"
        class="place-search__input"
        type="text"
        placeholder="搜索地点，如 丹东市"
        autocomplete="off"
        spellcheck="false"
        :disabled="disabled"
        @focus="onFocus"
        @keydown="onKeydown"
      />
      <button
        v-if="query"
        class="place-search__clear"
        type="button"
        title="清除"
        :disabled="disabled"
        @click="clearQuery"
      >
        ×
      </button>
    </div>

    <div v-if="panelOpen && query.trim()" class="place-search__panel">
      <div v-if="loading" class="place-search__hint">正在搜索…</div>
      <div v-else-if="errorText" class="place-search__hint is-error">{{ errorText }}</div>
      <div v-else-if="query.trim() && !results.length" class="place-search__hint">未找到该地点</div>
      <button
        v-for="(item, index) in results"
        :key="`${item.place_id}-${item.lng}-${item.lat}-${index}`"
        class="place-search__item"
        :class="{ 'is-active': index === activeIndex }"
        type="button"
        @mouseenter="activeIndex = index"
        @click="selectResult(item)"
      >
        <span class="place-search__item-name">{{ item.title }}</span>
        <span v-if="item.subtitle" class="place-search__item-sub">{{ item.subtitle }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { ElMessage } from "element-plus";
import { getMapInstance } from "@/assets/util/index";
import { searchPlaces, type PlaceHit } from "./nominatim";

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false,
  },
});

const query = ref("");
const results = ref<PlaceHit[]>([]);
const loading = ref(false);
const errorText = ref("");
const panelOpen = ref(false);
const activeIndex = ref(0);
const inputRef = ref<HTMLInputElement | null>(null);

let debounceTimer: ReturnType<typeof setTimeout> | null = null;
let abortCtrl: AbortController | null = null;
let searchSeq = 0;
let skipQueryWatch = false;

const runSearch = async (text: string) => {
  const seq = ++searchSeq;
  abortCtrl?.abort();
  abortCtrl = new AbortController();
  loading.value = true;
  errorText.value = "";
  try {
    const hits = await searchPlaces(text, abortCtrl.signal);
    if (seq !== searchSeq) return;
    results.value = hits;
    activeIndex.value = 0;
  } catch (err: any) {
    if (err?.name === "AbortError") return;
    if (seq !== searchSeq) return;
    results.value = [];
    errorText.value = "搜索失败，请稍后重试";
  } finally {
    if (seq === searchSeq) loading.value = false;
  }
};

watch(query, (val) => {
  if (skipQueryWatch) return;
  if (debounceTimer) clearTimeout(debounceTimer);
  const text = val.trim();
  if (!text) {
    results.value = [];
    errorText.value = "";
    loading.value = false;
    panelOpen.value = false;
    return;
  }
  panelOpen.value = true;
  debounceTimer = setTimeout(() => runSearch(text), 450);
});

const onFocus = () => {
  if (props.disabled) return;
  if (query.value.trim()) panelOpen.value = true;
};

const clearQuery = () => {
  query.value = "";
  results.value = [];
  errorText.value = "";
  panelOpen.value = false;
  inputRef.value?.focus();
};

const flyToHit = (hit: PlaceHit) => {
  const map = getMapInstance();
  if (!map) {
    ElMessage.warning("地图尚未就绪");
    return;
  }
  const span = Math.max(hit.ymax - hit.ymin, hit.xmax - hit.xmin);
  if (span > 0.02) {
    map.flyToExtent(
      { xmin: hit.xmin, xmax: hit.xmax, ymin: hit.ymin, ymax: hit.ymax },
      { scale: 1.35, duration: 2 }
    );
    return;
  }
  map.flyToPoint([hit.lng, hit.lat], { radius: 60000, duration: 2 });
};

const selectResult = (hit: PlaceHit) => {
  skipQueryWatch = true;
  if (debounceTimer) {
    clearTimeout(debounceTimer);
    debounceTimer = null;
  }
  abortCtrl?.abort();
  searchSeq += 1;
  query.value = hit.title;
  results.value = [];
  errorText.value = "";
  loading.value = false;
  panelOpen.value = false;
  inputRef.value?.blur();
  flyToHit(hit);
  nextTick(() => {
    skipQueryWatch = false;
    panelOpen.value = false;
    results.value = [];
  });
};

const onKeydown = (e: KeyboardEvent) => {
  if (e.key === "Escape") {
    panelOpen.value = false;
    inputRef.value?.blur();
    return;
  }
  if (!results.value.length) {
    if (e.key === "Enter" && query.value.trim()) runSearch(query.value.trim());
    return;
  }
  if (e.key === "ArrowDown") {
    e.preventDefault();
    activeIndex.value = (activeIndex.value + 1) % results.value.length;
  } else if (e.key === "ArrowUp") {
    e.preventDefault();
    activeIndex.value = (activeIndex.value - 1 + results.value.length) % results.value.length;
  } else if (e.key === "Enter") {
    e.preventDefault();
    const hit = results.value[activeIndex.value];
    if (hit) selectResult(hit);
  }
};

const rootRef = ref<HTMLElement | null>(null);

const onDocMouseDown = (e: MouseEvent) => {
  if (!rootRef.value?.contains(e.target as Node)) {
    panelOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener("mousedown", onDocMouseDown);
});

onBeforeUnmount(() => {
  document.removeEventListener("mousedown", onDocMouseDown);
  if (debounceTimer) clearTimeout(debounceTimer);
  abortCtrl?.abort();
});
</script>

<style scoped lang="scss">
.place-search {
  position: relative;
  width: min(360px, 100%);
  flex: 1;
  max-width: 360px;
  min-width: 180px;
  pointer-events: all;
}

.place-search__field {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 38px;
  padding: 0 10px 0 12px;
  border-radius: 999px;
  background: rgba(8, 12, 18, 0.55);
  border: 1px solid rgba(180, 200, 220, 0.16);
  box-sizing: border-box;
}

.place-search.is-open .place-search__field,
.place-search__field:focus-within {
  border-color: rgba(126, 200, 255, 0.45);
  background: rgba(8, 12, 18, 0.78);
}

.place-search__icon {
  width: 16px;
  height: 16px;
  color: var(--gotham-text-muted, #8b8790);
  flex-shrink: 0;
  display: inline-flex;

  svg {
    width: 16px;
    height: 16px;
  }
}

.place-search__input {
  flex: 1;
  min-width: 0;
  height: 100%;
  border: none;
  outline: none;
  background: transparent;
  color: #e8e2d2;
  font-family: inherit;
  font-size: 12px;
  line-height: 1.2;

  &::placeholder {
    color: #5c5863;
  }

  &:disabled {
    cursor: default;
  }
}

.place-search__clear {
  width: 18px;
  height: 18px;
  border: none;
  border-radius: 50%;
  background: transparent;
  color: #8b8790;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  flex-shrink: 0;

  &:hover {
    color: #e8e2d2;
  }
}

.place-search__panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  max-height: 280px;
  overflow-y: auto;
  padding: 6px;
  border-radius: 12px;
  background: rgba(10, 14, 20, 0.94);
  border: 1px solid rgba(232, 226, 210, 0.12);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(18px);
  z-index: 1400;
  box-sizing: border-box;
}

.place-search__hint {
  padding: 10px 12px;
  font-size: 12px;
  color: #8b8790;

  &.is-error {
    color: #c45c4a;
  }
}

.place-search__item {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  padding: 8px 10px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #e8e2d2;
  text-align: left;
  cursor: pointer;

  &.is-active,
  &:hover {
    background: rgba(212, 160, 23, 0.15);
  }
}

.place-search__item-name {
  font-size: 12px;
  font-weight: 600;
}

.place-search__item-sub {
  font-size: 11px;
  color: #8b8790;
  line-height: 1.35;
}
</style>
