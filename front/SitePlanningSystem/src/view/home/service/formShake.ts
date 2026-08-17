export function shakeElements(targets: Array<HTMLElement | null | undefined>) {
  requestAnimationFrame(() => {
    targets.forEach((target) => {
      if (!target) return;
      target.classList.remove("field-shake");
      void target.offsetWidth;
      target.classList.add("field-shake");
      const onEnd = () => {
        target.classList.remove("field-shake");
        target.removeEventListener("animationend", onEnd);
      };
      target.addEventListener("animationend", onEnd);
    });
  });
}

/** Shake invalid form controls when validation fails (no error text). */
export function shakeInvalidFormFields(formEl: { $el?: HTMLElement } | HTMLElement | null | undefined) {
  const run = () => {
    const root = formEl && "$el" in formEl ? formEl.$el : (formEl as HTMLElement | undefined);
    if (!root) return;

    const items = root.querySelectorAll(".el-form-item.is-error");
    items.forEach((item) => {
      const target =
        (item.querySelector(".el-input__wrapper, .el-select__wrapper, .el-textarea__inner") as HTMLElement | null) ||
        (item.querySelector(".el-form-item__content") as HTMLElement | null);
      if (!target) return;

      target.classList.remove("field-shake");
      void target.offsetWidth;
      target.classList.add("field-shake");

      const onEnd = () => {
        target.classList.remove("field-shake");
        target.removeEventListener("animationend", onEnd);
      };
      target.addEventListener("animationend", onEnd);
    });
  };

  requestAnimationFrame(run);
}
