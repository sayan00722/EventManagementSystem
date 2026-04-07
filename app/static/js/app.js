document.addEventListener("DOMContentLoaded", () => {
    const numericInputs = document.querySelectorAll("input[type='number']");
    numericInputs.forEach((input) => {
        input.addEventListener("wheel", (event) => event.target.blur());
    });

    const toasts = document.querySelectorAll("[data-toast='true']");
    toasts.forEach((toast, idx) => {
        setTimeout(() => {
            toast.classList.add("toast-hide");
            setTimeout(() => toast.remove(), 350);
        }, 3000 + idx * 180);
    });

    const toggles = document.querySelectorAll(".toggle-password");
    toggles.forEach((button) => {
        button.addEventListener("click", () => {
            const targetId = button.getAttribute("data-target");
            const target = document.getElementById(targetId);
            if (!target) {
                return;
            }
            const makeText = target.type === "password";
            target.type = makeText ? "text" : "password";
            button.textContent = makeText ? "Hide" : "Show";
        });
    });

    const userSelect = document.getElementById("update_user_id");
    if (userSelect) {
        userSelect.addEventListener("change", () => {
            const selected = userSelect.options[userSelect.selectedIndex];
            const nameField = document.getElementById("update_user_name");
            const emailField = document.getElementById("update_user_email");
            if (nameField) {
                nameField.value = selected?.dataset?.name || "";
            }
            if (emailField) {
                emailField.value = selected?.dataset?.email || "";
            }
        });
    }

    const vendorSelect = document.getElementById("update_vendor_id");

    const setupTagInput = (container) => {
        const hidden = container.querySelector("[data-tag-hidden]");
        const text = container.querySelector("[data-tag-text]");
        const list = container.querySelector("[data-tag-list]");

        if (!hidden || !text || !list) {
            return null;
        }

        const state = { items: [] };

        const sync = () => {
            hidden.value = state.items.join(", ");
            list.innerHTML = "";
            state.items.forEach((item, index) => {
                const chip = document.createElement("span");
                chip.className = "tag-chip";
                chip.textContent = item;

                const removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.className = "tag-remove";
                removeBtn.textContent = "x";
                removeBtn.addEventListener("click", () => {
                    state.items.splice(index, 1);
                    sync();
                });

                chip.appendChild(removeBtn);
                list.appendChild(chip);
            });
        };

        const pushToken = (value) => {
            const token = value.trim();
            if (!token) {
                return;
            }
            const exists = state.items.some((item) => item.toLowerCase() === token.toLowerCase());
            if (!exists) {
                state.items.push(token);
                sync();
            }
        };

        text.addEventListener("keydown", (event) => {
            if (event.key === "," || event.key === "Enter") {
                event.preventDefault();
                pushToken(text.value.replace(/,+$/, ""));
                text.value = "";
            }
        });

        text.addEventListener("blur", () => {
            if (text.value.trim()) {
                pushToken(text.value);
                text.value = "";
            }
        });

        const setItemsFromString = (rawValue) => {
            state.items = [];
            (rawValue || "")
                .split(",")
                .map((s) => s.trim())
                .filter(Boolean)
                .forEach((item) => {
                    const exists = state.items.some((x) => x.toLowerCase() === item.toLowerCase());
                    if (!exists) {
                        state.items.push(item);
                    }
                });
            sync();
        };

        sync();
        return { setItemsFromString };
    };

    const tagContainers = document.querySelectorAll("[data-tag-input]");
    const tagApis = new Map();
    tagContainers.forEach((container) => {
        const api = setupTagInput(container);
        if (api) {
            tagApis.set(container.id || `tag-${Math.random()}`, api);
        }
    });

    if (vendorSelect) {
        vendorSelect.addEventListener("change", () => {
            const selected = vendorSelect.options[vendorSelect.selectedIndex];
            const nameField = document.getElementById("update_vendor_name");
            const emailField = document.getElementById("update_vendor_email");
            const categoryField = document.getElementById("update_vendor_category");
            const contactField = document.getElementById("update_vendor_contact");

            if (nameField) {
                nameField.value = selected?.dataset?.name || "";
            }
            if (emailField) {
                emailField.value = selected?.dataset?.email || "";
            }
            if (categoryField) {
                categoryField.value = selected?.dataset?.category || "Catering";
            }
            if (contactField) {
                contactField.value = selected?.dataset?.contact || "";
            }

            const rawItems = selected?.dataset?.sellItems || "";
            const updateItemsContainer = document.getElementById("update_vendor_items");
            if (updateItemsContainer) {
                const api = Array.from(tagApis.entries()).find(([id]) => id === "update_vendor_items")?.[1];
                if (api) {
                    api.setItemsFromString(rawItems);
                }
            }
        });
    }

    const userMembershipSelect = document.getElementById("user_membership_id");
    const userMembershipData = document.getElementById("user_membership_data");
    if (userMembershipSelect || userMembershipData) {
        const currentDuration = document.getElementById("user_membership_duration_current");
        const startDate = document.getElementById("user_membership_start");
        const endDate = document.getElementById("user_membership_end");
        const extensionSelect = document.getElementById("user_membership_extension");
        const projectedEndDate = document.getElementById("user_membership_end_projected");

        const formatDate = (dateObj) => {
            if (!(dateObj instanceof Date) || Number.isNaN(dateObj.getTime())) {
                return "";
            }
            const y = dateObj.getFullYear();
            const m = String(dateObj.getMonth() + 1).padStart(2, "0");
            const d = String(dateObj.getDate()).padStart(2, "0");
            return `${y}-${m}-${d}`;
        };

        const parseDate = (value) => {
            if (!value) {
                return null;
            }
            const normalized = value.includes("T") ? value : `${value}T00:00:00`;
            const parsed = new Date(normalized);
            return Number.isNaN(parsed.getTime()) ? null : parsed;
        };

        const applyDuration = (baseDate, durationLabel) => {
            if (!baseDate) {
                return null;
            }
            const result = new Date(baseDate.getTime());
            const lower = (durationLabel || "").toLowerCase();
            if (lower.includes("2 year")) {
                result.setFullYear(result.getFullYear() + 2);
            } else if (lower.includes("1 year")) {
                result.setFullYear(result.getFullYear() + 1);
            } else {
                result.setMonth(result.getMonth() + 6);
            }
            return result;
        };

        const getMembershipDataset = () => {
            if (userMembershipSelect) {
                return userMembershipSelect.options[userMembershipSelect.selectedIndex]?.dataset || null;
            }
            if (userMembershipData) {
                return userMembershipData.dataset;
            }
            return null;
        };

        const updateProjectedEnd = () => {
            if (!projectedEndDate) {
                return;
            }
            const data = getMembershipDataset();
            const baseDate = parseDate(data?.end || "");
            const projected = applyDuration(baseDate, extensionSelect?.value || "6 months");
            projectedEndDate.value = formatDate(projected);
        };

        const updateMembershipFields = () => {
            const data = getMembershipDataset();
            if (currentDuration) {
                currentDuration.value = data?.duration || "";
            }
            if (startDate) {
                startDate.value = data?.start || "";
            }
            if (endDate) {
                endDate.value = data?.end || "";
            }
            updateProjectedEnd();
        };

        if (userMembershipSelect) {
            userMembershipSelect.addEventListener("change", updateMembershipFields);
        }
        if (extensionSelect) {
            extensionSelect.addEventListener("change", updateProjectedEnd);
        }
        updateMembershipFields();
    }
});
