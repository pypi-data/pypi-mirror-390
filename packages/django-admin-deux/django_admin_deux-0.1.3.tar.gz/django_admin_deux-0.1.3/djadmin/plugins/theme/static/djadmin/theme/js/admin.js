/**
 * django-admin-deux JavaScript
 * Handles mobile menu, bulk actions, and dark mode
 */

(function() {
  'use strict';

  // Initialize on DOM ready
  document.addEventListener('DOMContentLoaded', function() {
    initDarkMode();
    initUserMenu();
    initBulkActions();
    initConfirmations();
    initMessages();
  });

  /**
   * Dark Mode Toggle
   *
   * Strategy:
   * 1. Check localStorage for saved preference
   * 2. Fall back to system preference (prefers-color-scheme)
   * 3. Apply .dark class to <html> element
   * 4. Save preference on toggle
   */
  function initDarkMode() {
    const toggle = document.getElementById('dark-mode-toggle');
    if (!toggle) return; // Dark mode not enabled (base template, no override)

    // Get saved preference or system preference
    const savedTheme = localStorage.getItem('theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = savedTheme === 'dark' || (!savedTheme && systemPrefersDark);

    // Apply theme
    applyTheme(isDark);

    // Toggle on click
    toggle.addEventListener('click', function() {
      const html = document.documentElement;
      const newIsDark = !html.classList.contains('dark');
      applyTheme(newIsDark);
      localStorage.setItem('theme', newIsDark ? 'dark' : 'light');
    });

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e) {
      // Only apply if no saved preference
      if (!localStorage.getItem('theme')) {
        applyTheme(e.matches);
      }
    });
  }

  function applyTheme(isDark) {
    const html = document.documentElement;
    if (isDark) {
      html.classList.add('dark');
    } else {
      html.classList.remove('dark');
    }
  }

  /**
   * User menu dropdown
   */
  function initUserMenu() {
    const menuToggle = document.getElementById('user-menu-toggle');
    const menuDropdown = document.getElementById('user-menu-dropdown');

    if (!menuToggle || !menuDropdown) return;

    // Toggle dropdown on click
    menuToggle.addEventListener('click', function(e) {
      e.stopPropagation();
      const isHidden = menuDropdown.hasAttribute('hidden');

      if (isHidden) {
        menuDropdown.removeAttribute('hidden');
        menuToggle.setAttribute('aria-expanded', 'true');
      } else {
        menuDropdown.setAttribute('hidden', '');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!menuToggle.contains(e.target) && !menuDropdown.contains(e.target)) {
        menuDropdown.setAttribute('hidden', '');
        menuToggle.setAttribute('aria-expanded', 'false');
      }
    });

    // Close dropdown on escape key
    document.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && !menuDropdown.hasAttribute('hidden')) {
        menuDropdown.setAttribute('hidden', '');
        menuToggle.setAttribute('aria-expanded', 'false');
        menuToggle.focus();
      }
    });
  }

  /**
   * Bulk action handling
   */
  function initBulkActions() {
    const selectAll = document.getElementById('select-all');
    const actionCheckboxes = document.querySelectorAll('input[name="_selected_action"]');
    const bulkForm = document.getElementById('bulk-action-form');

    // Select all functionality
    if (selectAll) {
      selectAll.addEventListener('change', function() {
        actionCheckboxes.forEach(function(checkbox) {
          checkbox.checked = selectAll.checked;
        });
        updateBulkActionState();
      });
    }

    // Update select-all state when individual checkboxes change
    actionCheckboxes.forEach(function(checkbox) {
      checkbox.addEventListener('change', function() {
        if (selectAll) {
          const allChecked = Array.from(actionCheckboxes).every(cb => cb.checked);
          const someChecked = Array.from(actionCheckboxes).some(cb => cb.checked);
          selectAll.checked = allChecked;
          selectAll.indeterminate = someChecked && !allChecked;
        }
        updateBulkActionState();
      });
    });

    // Bulk form submission validation
    if (bulkForm) {
      bulkForm.addEventListener('submit', function(e) {
        const selected = document.querySelectorAll('input[name="_selected_action"]:checked');
        if (selected.length === 0) {
          e.preventDefault();
          alert('Please select at least one item.');
          return false;
        }
      });
    }
  }

  /**
   * Update bulk action button state
   */
  function updateBulkActionState() {
    const selected = document.querySelectorAll('input[name="_selected_action"]:checked');
    const bulkButtons = document.querySelectorAll('.admin > main > form > menu button');
    const countEl = document.getElementById('selected-count');

    // Update count
    if (countEl) {
      countEl.textContent = selected.length;
    }

    // Enable/disable buttons
    bulkButtons.forEach(function(button) {
      button.disabled = selected.length === 0;
    });
  }

  /**
   * Confirmation dialogs
   */
  function initConfirmations() {
    const confirmButtons = document.querySelectorAll('[data-confirm]');

    confirmButtons.forEach(function(button) {
      button.addEventListener('click', function(e) {
        const message = button.getAttribute('data-confirm');
        if (!confirm(message)) {
          e.preventDefault();
          return false;
        }
      });
    });
  }

  /**
   * Auto-dismiss messages
   */
  function initMessages() {
    const messages = document.querySelectorAll('[role="alert"]');

    messages.forEach(function(message) {
      const dismissButton = message.querySelector('button[aria-label="Dismiss"]');

      // Manual dismiss
      if (dismissButton) {
        dismissButton.addEventListener('click', function() {
          message.remove();
        });
      }

      // Auto-dismiss after 5 seconds
      setTimeout(function() {
        if (message.parentElement) {
          message.style.transition = 'opacity 0.3s';
          message.style.opacity = '0';
          setTimeout(function() {
            message.remove();
          }, 300);
        }
      }, 5000);
    });
  }
})();
