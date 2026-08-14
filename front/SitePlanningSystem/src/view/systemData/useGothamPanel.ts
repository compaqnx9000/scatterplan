import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";

export function formatDecimal6(val: any) {
  if (val === null || val === undefined || val === "") return "";
  const n = Number(val);
  if (!Number.isFinite(n)) return val;
  if (Number.isInteger(n)) return String(n);
  return n.toFixed(6);
}

export function useGothamPanel(panelWidth = 1080) {
  const router = useRouter();
  const panelRef = ref<HTMLElement | null>(null);
  const panelPos = ref({ x: 24, y: 72 });
  const dragging = ref(false);
  const dragOffset = ref({ x: 0, y: 0 });

  const panelStyle = computed(() => ({
    left: `${panelPos.value.x}px`,
    top: `${panelPos.value.y}px`,
    width: `${Math.min(panelWidth, window.innerWidth - 48)}px`,
  }));

  const getDefaultPanelPos = (size?: { width: number; height: number }) => {
    const width = size?.width ?? Math.min(panelWidth, window.innerWidth - 48);
    const height = size?.height ?? 560;
    return {
      x: Math.max(24, Math.round((window.innerWidth - width) / 2)),
      y: Math.max(72, Math.round((window.innerHeight - height) / 2)),
    };
  };

  const centerPanel = async () => {
    panelPos.value = getDefaultPanelPos();
    await nextTick();
    const el = panelRef.value;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    panelPos.value = getDefaultPanelPos({ width: rect.width, height: rect.height });
  };

  const startDrag = (e: MouseEvent) => {
    if (e.button !== 0) return;
    dragging.value = true;
    dragOffset.value = {
      x: e.clientX - panelPos.value.x,
      y: e.clientY - panelPos.value.y,
    };
    window.addEventListener("mousemove", onDrag);
    window.addEventListener("mouseup", stopDrag);
  };

  const onDrag = (e: MouseEvent) => {
    if (!dragging.value) return;
    const width = Math.min(panelWidth, window.innerWidth - 48);
    const maxX = Math.max(0, window.innerWidth - width);
    const maxY = Math.max(0, window.innerHeight - 80);
    panelPos.value = {
      x: Math.min(maxX, Math.max(0, e.clientX - dragOffset.value.x)),
      y: Math.min(maxY, Math.max(0, e.clientY - dragOffset.value.y)),
    };
  };

  const stopDrag = () => {
    dragging.value = false;
    window.removeEventListener("mousemove", onDrag);
    window.removeEventListener("mouseup", stopDrag);
  };

  const handleClose = () => {
    router.push("/");
  };

  const onEsc = (e: KeyboardEvent) => {
    if (e.key === "Escape") handleClose();
  };

  onMounted(() => {
    centerPanel();
    window.addEventListener("keydown", onEsc);
  });

  onBeforeUnmount(() => {
    stopDrag();
    window.removeEventListener("keydown", onEsc);
  });

  return {
    panelRef,
    panelStyle,
    startDrag,
    handleClose,
    centerPanel,
  };
}
