document.addEventListener('DOMContentLoaded', () => {
    const selects = document.querySelectorAll('.async-select');

    selects.forEach(select => {
      // ----- idempotency guards -----
      if (select.dataset.asyncSelectInit === '1') return;              // already inited by us
      if (select.previousElementSibling?.classList?.contains('async-select-search')) return; // existing search input

      // If jQuery + Select2 is present and already attached, don't init our widget
      if (typeof window.jQuery === 'function' && window.jQuery(select).data('select2')) return;

      select.dataset.asyncSelectInit = '1';
      // --------------------------------

      const wrapper = select.parentNode;
      wrapper.classList.add('async-select-wrapper');
      // wrapper.classList.add('form-floating');

      const apiEndpoint = select.dataset.apiEndpoint;
      const searchField = select.dataset.searchField;
      const selectedValue = select.dataset.selected;
      const model = select.dataset.model;
      const minLength = select.dataset.minLength;
      // Create search input
      const searchInput = document.createElement('input');
      searchInput.type = 'text';
      searchInput.className = 'async-select-search form-control';
      if (select.dataset.required === 'True') {
        searchInput.required = true;
      }
      wrapper.insertBefore(searchInput, select);
      // wrapper.prepend(searchInput);
      const label = wrapper.querySelector('label');
      if (label) {
        label.textContent = `${label.textContent}: search (${minLength} characters minimum)`;
      }

      // Create dropdown container
      const dropdown = document.createElement('div');
      dropdown.className = 'async-select-dropdown dropdown-menu';
      wrapper.appendChild(dropdown);

      // Hide original select
      select.style.display = 'none';

      // Track keyboard navigation state
      let highlightedIndex = -1;
      let currentOptions = [];

      // Function to select an option by index
      const selectOption = (index) => {
          if (index < 0 || index >= currentOptions.length) return;
          const option = currentOptions[index];
          if (option && option.click) {
              option.click();
          }
      };

      // Function to highlight an option by index
      const highlightOption = (index) => {
          // Remove highlight from all options
          currentOptions.forEach(opt => {
              opt.classList.remove('active', 'highlighted', 'focused');
          });

          if (index >= 0 && index < currentOptions.length) {
              currentOptions[index].classList.add('active', 'highlighted', 'focused');
              // Scroll into view if needed
              currentOptions[index].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
          }

          highlightedIndex = index;
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
                  currentOptions = [];
                  highlightedIndex = -1;
                  return;
              }

              try {
                  const response = await fetch(`${apiEndpoint}?q=${encodeURIComponent(query)}&field=${searchField}&model=${model}`);
                  if (!response.ok) {
                      throw new Error(`HTTP ${response.status}`);
                  }

                  const data = await response.json().catch(() => null);

                  dropdown.innerHTML = '';
                  currentOptions = [];
                  highlightedIndex = -1;

                  // Normalize possible response shapes into an array
                  const items = Array.isArray(data)
                      ? data
                      : (data && Array.isArray(data.results))
                          ? data.results
                          : (data && Array.isArray(data.items))
                              ? data.items
                              : [];

                  if (!items.length) {
                      const empty = document.createElement('div');
                      empty.className = 'async-select-empty dropdown-item disabled';
                      empty.textContent = 'No results';
                      dropdown.appendChild(empty);
                      dropdown.classList.add('show');
                      return;
                  }

                  items.forEach(item => {
                      const option = document.createElement('div');
                      option.className = 'async-select-option dropdown-item';
                      option.dataset.value = item.id ?? item.value ?? '';
                      option.textContent = item.text ?? item.label ?? String(item);
                      option.addEventListener('click', () => {
                          const chosenValue = option.dataset.value;
                          const chosenText = option.textContent;

                          // Ensure the <select> has a real option matching the chosen value
                          let chosenOption = select.querySelector('option.async-select-chosen');
                          if (!chosenOption) {
                              // Create a dedicated option we control
                              chosenOption = document.createElement('option');
                              chosenOption.className = 'async-select-chosen';
                              select.appendChild(chosenOption);
                          }
                          chosenOption.value = chosenValue ?? '';
                          chosenOption.textContent = chosenText ?? '';

                          // Mark only our chosen option as selected; unselect any placeholder
                          [...select.options].forEach(o => { o.selected = false; });
                          chosenOption.selected = true;

                          // Update select.value and fire change for any listeners
                          select.value = chosenOption.value;
                          select.dispatchEvent(new Event('change', { bubbles: true }));

                          // Reflect the choice in the visible input
                          searchInput.value = chosenText;

                          // Close dropdown
                          dropdown.innerHTML = '';
                          dropdown.classList.remove('show');
                          currentOptions = [];
                          highlightedIndex = -1;
                      });
                      dropdown.appendChild(option);
                      currentOptions.push(option);
                  });
                  dropdown.classList.add('show');
                  // Highlight first option when dropdown appears
                  if (currentOptions.length > 0) {
                      highlightOption(0);
                  }
              } catch (error) {
                  console.error('Error fetching results:', error);
              }
          }, 300);
      });

      // Handle keyboard navigation when dropdown is visible
      searchInput.addEventListener('keydown', (e) => {
          if (!dropdown.classList.contains('show') || currentOptions.length === 0) {
              return;
          }

          switch (e.key) {
              case 'ArrowDown':
                  e.preventDefault();
                  if (highlightedIndex < currentOptions.length - 1) {
                      highlightOption(highlightedIndex + 1);
                  } else {
                      highlightOption(0); // Wrap to top
                  }
                  break;

              case 'ArrowUp':
                  e.preventDefault();
                  if (highlightedIndex > 0) {
                      highlightOption(highlightedIndex - 1);
                  } else {
                      highlightOption(currentOptions.length - 1); // Wrap to bottom
                  }
                  break;

              case 'Enter':
                  e.preventDefault();
                  if (highlightedIndex >= 0 && highlightedIndex < currentOptions.length) {
                      selectOption(highlightedIndex);
                  }
                  break;

              case 'Escape':
                  e.preventDefault();
                  dropdown.innerHTML = '';
                  dropdown.classList.remove('show');
                  currentOptions = [];
                  highlightedIndex = -1;
                  break;
          }
      });

      // Close dropdown when clicking outside
      document.addEventListener('click', (e) => {
          if (!select.parentNode.contains(e.target)) {
              dropdown.innerHTML = '';
              dropdown.classList.remove('show');
              currentOptions = [];
              highlightedIndex = -1;
          }
      });

      // Initialize with selected value
      if (selectedValue) {
          searchInput.value = select.options[select.selectedIndex].text;
      }
    });
});