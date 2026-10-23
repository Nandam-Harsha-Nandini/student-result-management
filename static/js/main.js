/**
 * EduResult Nexus / ApexEdu Portal - Main Client JavaScript
 */

document.addEventListener("DOMContentLoaded", () => {
  // Mobile Nav Toggle
  const menuToggle = document.getElementById("menuToggle");
  const navLinks = document.getElementById("navLinks");
  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", () => {
      navLinks.classList.toggle("show");
    });
  }

  // Auto-dismiss alert notifications after 5 seconds
  const alerts = document.querySelectorAll(".alert");
  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.style.opacity = "0";
      alert.style.transform = "translateY(-10px)";
      alert.style.transition = "all 0.4s ease";
      setTimeout(() => alert.remove(), 400);
    }, 5500);
  });

  // Modal helpers
  window.openModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("active");
      document.body.style.overflow = "hidden";
    }
  };

  window.closeModal = function (modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("active");
      document.body.style.overflow = "";
    }
  };

  // Close modals when clicking backdrop or pressing Esc
  document.querySelectorAll(".modal-overlay").forEach((overlay) => {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.classList.remove("active");
        document.body.style.overflow = "";
      }
    });
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal-overlay.active").forEach((modal) => {
        modal.classList.remove("active");
      });
      document.body.style.overflow = "";
    }
  });

  // Live dynamic calculation for Add/Edit Student form
  const markInputs = document.querySelectorAll(".mark-input");
  if (markInputs.length > 0) {
    const totalDisplay = document.getElementById("calcTotal");
    const percentDisplay = document.getElementById("calcPercent");
    const gradeDisplay = document.getElementById("calcGrade");

    function updateCalculations() {
      let total = 0;
      let valid = true;
      let passedAll = true;

      markInputs.forEach((input) => {
        const val = parseFloat(input.value) || 0;
        total += val;
        if (val < 35) passedAll = false;
      });

      const percentage = (total / markInputs.length).toFixed(2);
      
      let letterGrade = "F";
      if (passedAll) {
        if (percentage >= 90) letterGrade = "A+";
        else if (percentage >= 80) letterGrade = "A";
        else if (percentage >= 70) letterGrade = "B+";
        else if (percentage >= 60) letterGrade = "B";
        else if (percentage >= 50) letterGrade = "C";
        else letterGrade = "D";
      }

      if (totalDisplay) totalDisplay.textContent = total.toFixed(1);
      if (percentDisplay) percentDisplay.textContent = percentage + "%";
      if (gradeDisplay) {
        gradeDisplay.textContent = letterGrade;
        gradeDisplay.className = `badge ${passedAll ? 'badge-pass' : 'badge-fail'}`;
      }
    }

    markInputs.forEach((inp) => {
      inp.addEventListener("input", updateCalculations);
    });
    updateCalculations();
  }

  // Quick Instant Roll Search Autocomplete / API
  const quickSearchInput = document.getElementById("quickSearchInput");
  const quickSearchResults = document.getElementById("quickSearchResults");
  if (quickSearchInput && quickSearchResults) {
    let debounceTimer;
    quickSearchInput.addEventListener("input", (e) => {
      clearTimeout(debounceTimer);
      const query = e.target.value.trim();
      if (query.length < 2) {
        quickSearchResults.innerHTML = "";
        quickSearchResults.style.display = "none";
        return;
      }

      debounceTimer = setTimeout(() => {
        fetch(`/api/quick-search/?q=${encodeURIComponent(query)}`)
          .then((res) => res.json())
          .then((data) => {
            if (data.results && data.results.length > 0) {
              quickSearchResults.innerHTML = data.results
                .map(
                  (s) => `
                <a href="${s.url}" class="search-result-item" style="display:flex;align-items:center;justify-content:space-between;padding:10px 14px;border-bottom:1px solid #f1f5f9;text-decoration:none;color:#0f172a;">
                  <div>
                    <div style="font-weight:700;font-size:0.92rem;">${s.name}</div>
                    <div style="font-size:0.8rem;color:#64748b;">Roll: ${s.roll_number} • ${s.department}</div>
                  </div>
                  <div style="text-align:right;">
                    <span class="badge ${s.status === 'Pass' ? 'badge-pass' : 'badge-fail'}">${s.status}</span>
                    <div style="font-size:0.8rem;font-weight:700;margin-top:2px;">${s.percentage}% (${s.grade})</div>
                  </div>
                </a>
              `
                )
                .join("");
              quickSearchResults.style.display = "block";
            } else {
              quickSearchResults.innerHTML = `<div style="padding:12px;color:#64748b;font-size:0.88rem;text-align:center;">No students matched "${query}"</div>`;
              quickSearchResults.style.display = "block";
            }
          })
          .catch((err) => console.error("Search error:", err));
      }, 300);
    });

    // Close search dropdown on click outside
    document.addEventListener("click", (e) => {
      if (!quickSearchInput.contains(e.target) && !quickSearchResults.contains(e.target)) {
        quickSearchResults.style.display = "none";
      }
    });
  }

  // 1-Click Demo Login Autofill Helpers
  window.fillDemo = function (role) {
    const userField = document.getElementById("id_username");
    const passField = document.getElementById("id_password");
    if (!userField || !passField) return;

    if (role === "faculty") {
      userField.value = "faculty";
      passField.value = "faculty123";
    } else if (role === "student") {
      userField.value = "student";
      passField.value = "student123";
    } else if (role === "admin") {
      userField.value = "admin";
      passField.value = "admin123";
    }

    const form = userField.closest("form");
    if (form) {
      // Highlight briefly
      userField.style.borderColor = "#10b981";
      passField.style.borderColor = "#10b981";
      setTimeout(() => form.submit(), 250);
    }
  };
});
