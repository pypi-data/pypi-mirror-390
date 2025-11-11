document.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('.async-select-many');

    selects.forEach(select => {
        // ----- idempotency guards -----
        if (select.dataset.asyncSelectManyInit === '1') return;
        select.dataset.asyncSelectManyInit = '1';
        // --------------------------------

        const wrapper = select.parentNode;
        if (!wrapper.classList.contains('async-select-many-wrapper')) {
            return; // Template structure not found
        }

        const apiEndpoint = select.dataset.apiEndpoint;
        const searchField = select.dataset.searchField;
        const model = select.dataset.model;
        const minLength = parseInt(select.dataset.minLength) || 3;

        const tagsContainer = wrapper.querySelector('.async-select-many-tags');
        const searchInput = wrapper.querySelector('.async-select-many-search');
        const dropdown = wrapper.querySelector('.async-select-many-dropdown');

        // Track currently focused option index
        let focusedOptionIndex = -1;

        // Get currently selected IDs
        const getSelectedIds = () => {
            return Array.from(select.querySelectorAll('option.async-select-many-chosen'))
                .map(opt => opt.value)
                .filter(v => v);
        };

        // Get all dropdown options
        const getDropdownOptions = () => {
            return Array.from(dropdown.querySelectorAll('.async-select-many-option'));
        };

        // Focus an option by index
        const focusOption = (index) => {
            const options = getDropdownOptions();
            if (options.length === 0) return;

            // Clamp index to valid range
            if (index < 0) index = 0;
            if (index >= options.length) index = options.length - 1;

            // Remove focus from all options
            options.forEach(opt => {
                opt.classList.remove('active', 'focused');
                opt.blur();
            });

            // Focus the target option
            focusedOptionIndex = index;
            const targetOption = options[index];
            if (targetOption) {
                targetOption.classList.add('active', 'focused');
                targetOption.focus();
                // Scroll into view if needed
                targetOption.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
            }
        };

        // Move focus to next option
        const focusNextOption = () => {
            const options = getDropdownOptions();
            if (options.length === 0) return;
            // If no option is focused yet, start with first option
            if (focusedOptionIndex < 0) {
                focusOption(0);
            } else {
                focusOption(focusedOptionIndex + 1);
            }
        };

        // Move focus to previous option
        const focusPreviousOption = () => {
            const options = getDropdownOptions();
            if (options.length === 0) return;
            // If no option is focused yet, start with last option
            if (focusedOptionIndex < 0) {
                focusOption(options.length - 1);
            } else {
                focusOption(focusedOptionIndex - 1);
            }
        };

        // Select the currently focused option
        const selectFocusedOption = () => {
            const options = getDropdownOptions();
            if (options.length === 0 || focusedOptionIndex < 0) return;
            const focusedOption = options[focusedOptionIndex];
            if (focusedOption) {
                const chosenValue = focusedOption.dataset.value;
                const chosenText = focusedOption.textContent;
                addTag(chosenValue, chosenText);
            }
        };

        // Create a tag element
        const createTag = (id, text) => {
            const tag = document.createElement('span');
            tag.className = 'async-select-many-tag';
            tag.dataset.value = id;

            const tagText = document.createElement('span');
            tagText.className = 'async-select-many-tag-text';
            tagText.textContent = text;

            const removeBtn = document.createElement('button');
            removeBtn.type = 'button';
            removeBtn.className = 'async-select-many-tag-remove';
            removeBtn.setAttribute('aria-label', `Remove ${text}`);
            removeBtn.setAttribute('tabindex', '0');
            removeBtn.textContent = '×';
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                removeTag(id);
            });
            removeBtn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    removeTag(id);
                }
            });

            tag.appendChild(tagText);
            tag.appendChild(removeBtn);
            return tag;
        };

        // Add a tag and update hidden select
        const addTag = (id, text) => {
            // Check if already selected
            if (getSelectedIds().includes(String(id))) {
                return;
            }

            // Add option to hidden select
            const option = document.createElement('option');
            option.value = id;
            option.textContent = text;
            option.className = 'async-select-many-chosen';
            option.selected = true;
            select.appendChild(option);

            // Add tag to UI
            const tag = createTag(id, text);
            tagsContainer.appendChild(tag);

            // Clear search input
            searchInput.value = '';

            // Close dropdown
            dropdown.innerHTML = '';
            dropdown.classList.remove('show');
            focusedOptionIndex = -1;

            // Fire change event
            select.dispatchEvent(new Event('change', { bubbles: true }));
        };

        // Remove a tag and update hidden select
        const removeTag = (id) => {
            // Remove option from hidden select
            const option = select.querySelector(`option[value="${id}"].async-select-many-chosen`);
            if (option) {
                option.remove();
            }

            // Remove tag from UI
            const tag = tagsContainer.querySelector(`.async-select-many-tag[data-value="${id}"]`);
            if (tag) {
                tag.remove();
            }

            // Return focus to search input
            searchInput.focus();

            // Fire change event
            select.dispatchEvent(new Event('change', { bubbles: true }));
        };

        // Initialize tags from existing options
        const initTags = () => {
            const existingOptions = select.querySelectorAll('option.async-select-many-chosen[selected]');
            const existingTagIds = Array.from(tagsContainer.querySelectorAll('.async-select-many-tag'))
                .map(tag => tag.dataset.value);

            existingOptions.forEach(option => {
                if (option.value) {
                    // Check if tag already exists (from template rendering)
                    if (!existingTagIds.includes(String(option.value))) {
                        // Create new tag if it doesn't exist
                        const tag = createTag(option.value, option.textContent);
                        tagsContainer.appendChild(tag);
                    } else {
                        // Attach event listener to existing tag's remove button
                        const existingTag = tagsContainer.querySelector(`.async-select-many-tag[data-value="${option.value}"]`);
                        if (existingTag) {
                            const removeBtn = existingTag.querySelector('.async-select-many-tag-remove');
                            if (removeBtn && !removeBtn.dataset.listenerAttached) {
                                // Ensure accessibility attributes
                                if (!removeBtn.hasAttribute('tabindex')) {
                                    removeBtn.setAttribute('tabindex', '0');
                                }
                                const tagText = existingTag.querySelector('.async-select-many-tag-text');
                                const tagTextContent = tagText ? tagText.textContent : option.textContent;
                                removeBtn.setAttribute('aria-label', `Remove ${tagTextContent}`);

                                removeBtn.addEventListener('click', (e) => {
                                    e.stopPropagation();
                                    removeTag(option.value);
                                });
                                removeBtn.addEventListener('keydown', (e) => {
                                    if (e.key === 'Enter' || e.key === ' ') {
                                        e.preventDefault();
                                        e.stopPropagation();
                                        removeTag(option.value);
                                    }
                                });
                                removeBtn.dataset.listenerAttached = '1';
                            }
                        }
                    }
                }
            });
        };

        // Handle search input
        let debounceTimer;
        searchInput.addEventListener('input', () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(async () => {
                const query = searchInput.value.trim();
                if (query.length < minLength) {
                    dropdown.innerHTML = '';
                    dropdown.classList.remove('show');
                    focusedOptionIndex = -1;
                    return;
                }

                try {
                    const response = await fetch(`${apiEndpoint}?q=${encodeURIComponent(query)}&field=${searchField}&model=${model}`);
                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}`);
                    }

                    const data = await response.json().catch(() => null);
                    dropdown.innerHTML = '';

                    // Normalize possible response shapes into an array
                    const items = Array.isArray(data)
                        ? data
                        : (data && Array.isArray(data.results))
                            ? data.results
                            : (data && Array.isArray(data.items))
                                ? data.items
                                : [];

                    // Filter out already-selected items
                    const selectedIds = getSelectedIds();
                    const filteredItems = items.filter(item => {
                        const itemId = String(item.id ?? item.value ?? '');
                        return !selectedIds.includes(itemId);
                    });

                    if (!filteredItems.length) {
                        const empty = document.createElement('div');
                        empty.className = 'async-select-many-empty dropdown-item disabled';
                        empty.textContent = 'No results';
                        dropdown.appendChild(empty);
                        dropdown.classList.add('show');
                        searchInput.focus();
                        return;
                    }

                    filteredItems.forEach(item => {
                        const option = document.createElement('div');
                        option.className = 'async-select-many-option dropdown-item';
                        option.dataset.value = item.id ?? item.value ?? '';
                        option.textContent = item.text ?? item.label ?? String(item);
                        option.setAttribute('tabindex', '0');
                        option.addEventListener('click', () => {
                            const chosenValue = option.dataset.value;
                            const chosenText = option.textContent;
                            addTag(chosenValue, chosenText);
                        });
                        option.addEventListener('keydown', (e) => {
                            if (e.key === 'Enter' || e.key === ' ') {
                                e.preventDefault();
                                const chosenValue = option.dataset.value;
                                const chosenText = option.textContent;
                                addTag(chosenValue, chosenText);
                            } else if (e.key === 'ArrowDown') {
                                e.preventDefault();
                                focusNextOption();
                            } else if (e.key === 'ArrowUp') {
                                e.preventDefault();
                                focusPreviousOption();
                            }
                        });
                        option.addEventListener('focus', () => {
                            const options = getDropdownOptions();
                            focusedOptionIndex = options.indexOf(option);
                            options.forEach(opt => opt.classList.remove('active', 'focused'));
                            option.classList.add('active', 'focused');
                        });
                        dropdown.appendChild(option);
                    });
                    dropdown.classList.add('show');
                    // Reset focused index when dropdown opens
                    focusedOptionIndex = -1;
                    searchInput.focus();
                } catch (error) {
                    console.error('Error fetching results:', error);
                }
            }, 300);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                dropdown.innerHTML = '';
                dropdown.classList.remove('show');
                focusedOptionIndex = -1;
            }
        });

        // Handle keyboard navigation
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                dropdown.innerHTML = '';
                dropdown.classList.remove('show');
                searchInput.value = '';
                focusedOptionIndex = -1;
            } else if (e.key === 'ArrowDown' && dropdown.classList.contains('show')) {
                e.preventDefault();
                focusNextOption();
            } else if (e.key === 'ArrowUp' && dropdown.classList.contains('show')) {
                e.preventDefault();
                focusPreviousOption();
            } else if ((e.key === 'Enter' || e.key === ' ') && dropdown.classList.contains('show')) {
                e.preventDefault();
                selectFocusedOption();
            }
        });

        // Initialize tags from existing options
        initTags();

        // Focus search input when clicking on the tags container
        const tagsContainerElement = wrapper.querySelector('.async-select-many-tags-container');
        if (tagsContainerElement) {
            tagsContainerElement.addEventListener('click', () => {
                if (document.activeElement !== searchInput) {
                    searchInput.focus();
                }
            });
        }
    });
});

