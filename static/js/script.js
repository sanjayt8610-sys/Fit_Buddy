/**
 * FitBuddy – AI Fitness Plan Generator
 * Modern Interactive Frontend Controller
 */

document.addEventListener('DOMContentLoaded', () => {
    initMobileNav();
    initFormValidation();
    initFeedbackForm();
    initSmoothScroll();
});

/* ==========================================================================
   1. Mobile Navigation
   ========================================================================== */
function initMobileNav() {
    const mobileToggle = document.getElementById('mobileToggle');
    const navLinks = document.getElementById('navLinks');

    if (mobileToggle && navLinks) {
        mobileToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileToggle.classList.toggle('open');
        });

        // Close on link click
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                mobileToggle.classList.remove('open');
            });
        });
    }
}

/* ==========================================================================
   2. Fitness Form Validation & Loading Experience
   ========================================================================== */
function initFormValidation() {
    const form = document.getElementById('fitnessForm');
    if (!form) return;

    const nameInput = document.getElementById('name');
    const userIdInput = document.getElementById('user_id');
    const ageInput = document.getElementById('age');
    const weightInput = document.getElementById('weight');
    const goalInput = document.getElementById('goal');
    const intensityInput = document.getElementById('intensity');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // Real-time input cleaning for user_id
    if (userIdInput) {
        userIdInput.addEventListener('input', (e) => {
            e.target.value = e.target.value.toLowerCase().replace(/[^a-z0-9_\-]/g, '');
        });
    }

    form.addEventListener('submit', (e) => {
        let isValid = true;

        // Reset errors
        document.querySelectorAll('.field-error').forEach(el => el.textContent = '');

        // 1. Name Validation
        if (!nameInput.value.trim() || nameInput.value.trim().length < 2) {
            document.getElementById('nameError').textContent = 'Please enter a valid full name (at least 2 characters).';
            isValid = false;
        }

        // 2. User ID Validation
        const userIdVal = userIdInput.value.trim();
        if (!userIdVal || userIdVal.length < 3) {
            document.getElementById('userIdError').textContent = 'User ID must be at least 3 characters long.';
            isValid = false;
        } else if (!/^[a-zA-Z0-9_\-]+$/.test(userIdVal)) {
            document.getElementById('userIdError').textContent = 'User ID can only contain letters, numbers, hyphens, and underscores.';
            isValid = false;
        }

        // 3. Age Validation
        const ageVal = parseInt(ageInput.value, 10);
        if (isNaN(ageVal) || ageVal < 13 || ageVal > 120) {
            document.getElementById('ageError').textContent = 'Age must be between 13 and 120 years.';
            isValid = false;
        }

        // 4. Weight Validation
        const weightVal = parseFloat(weightInput.value);
        if (isNaN(weightVal) || weightVal < 20 || weightVal > 350) {
            document.getElementById('weightError').textContent = 'Weight must be between 20 kg and 350 kg.';
            isValid = false;
        }

        // 5. Goal Validation
        if (!goalInput.value) {
            document.getElementById('goalError').textContent = 'Please select a primary fitness goal.';
            isValid = false;
        }

        // 6. Intensity Validation
        if (!intensityInput.value) {
            document.getElementById('intensityError').textContent = 'Please select a workout intensity level.';
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            // Scroll to top of form
            form.scrollIntoView({ behavior: 'smooth', block: 'center' });
            return;
        }

        // Show loading state and animate steps
        if (loadingOverlay) {
            loadingOverlay.classList.remove('hidden');
            loadingOverlay.setAttribute('aria-hidden', 'false');
            startLoadingProgress();
        }
    });
}

function startLoadingProgress() {
    const progressFill = document.getElementById('progressBarFill');
    const dynamicText = document.getElementById('loadingDynamicText');
    const step2 = document.getElementById('step2Badge');
    const step3 = document.getElementById('step3Badge');

    let percent = 15;
    const interval = setInterval(() => {
        if (percent < 90) {
            percent += Math.floor(Math.random() * 12) + 5;
            if (progressFill) progressFill.style.width = percent + '%';

            if (percent > 40 && step2) {
                step2.classList.add('active');
                if (dynamicText) dynamicText.textContent = 'Generating 7-Day exercise regimen & recovery cycles...';
            }
            if (percent > 75 && step3) {
                step3.classList.add('active');
                if (dynamicText) dynamicText.textContent = 'Formulating targeted nutrition and hydration targets...';
            }
        }
    }, 400);
}

/* ==========================================================================
   3. Feedback Form Helpers
   ========================================================================== */
function initFeedbackForm() {
    const feedbackTextarea = document.getElementById('feedback');
    const charCounter = document.getElementById('charCounter');
    const feedbackForm = document.getElementById('feedbackForm');
    const feedbackOverlay = document.getElementById('feedbackLoadingOverlay');

    if (feedbackTextarea && charCounter) {
        const updateCount = () => {
            const count = feedbackTextarea.value.length;
            charCounter.textContent = `${count} / 1000`;
        };
        feedbackTextarea.addEventListener('input', updateCount);
        updateCount();
    }

    if (feedbackForm) {
        feedbackForm.addEventListener('submit', (e) => {
            const text = feedbackTextarea ? feedbackTextarea.value.trim() : '';
            if (!text || text.length < 3) {
                e.preventDefault();
                const err = document.getElementById('feedbackError');
                if (err) err.textContent = 'Please enter specific feedback to help AI modify your plan.';
                return;
            }

            if (feedbackOverlay) {
                feedbackOverlay.classList.remove('hidden');
                feedbackOverlay.setAttribute('aria-hidden', 'false');
            }
        });
    }
}

function appendFeedbackTag(text) {
    const textarea = document.getElementById('feedback');
    if (!textarea) return;

    let current = textarea.value.trim();
    if (current.length > 0) {
        textarea.value = current + '. ' + text;
    } else {
        textarea.value = text;
    }

    const charCounter = document.getElementById('charCounter');
    if (charCounter) {
        charCounter.textContent = `${textarea.value.length} / 1000`;
    }
    textarea.focus();
}

/* ==========================================================================
   4. Clipboard & Copying
   ========================================================================== */
function copyPlanToClipboard() {
    const printable = document.getElementById('printablePlan');
    const copyBtnText = document.getElementById('copyBtnText');

    if (!printable) {
        showToast('No plan text available to copy.');
        return;
    }

    // Extract text representation
    const text = printable.innerText;
    navigator.clipboard.writeText(text).then(() => {
        if (copyBtnText) copyBtnText.textContent = 'Copied! ✓';
        showToast('Workout plan copied to clipboard!');
        setTimeout(() => {
            if (copyBtnText) copyBtnText.textContent = 'Copy Plan';
        }, 3000);
    }).catch(() => {
        showToast('Failed to copy. Please select text manually.');
    });
}

function showToast(message) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.innerHTML = `<span>⚡</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

/* ==========================================================================
   5. Admin Modal Inspector & Deletion
   ========================================================================== */
function inspectPlan(userId, name, goal, intensity, age, weight, isUpdated, hasPlan) {
    const modal = document.getElementById('inspectModal');
    const modalName = document.getElementById('modalUserName');
    const modalMeta = document.getElementById('modalUserMeta');
    const modalBody = document.getElementById('modalPlanContent');
    const externalLink = document.getElementById('modalExternalLink');

    if (!modal || !modalBody) return;

    modalName.textContent = `${name} (${userId})`;
    modalMeta.textContent = `Age: ${age} yrs | Weight: ${weight} kg | Goal: ${goal} | Intensity: ${intensity}`;
    externalLink.href = `/result/${userId}`;

    modal.classList.remove('hidden');
    modal.setAttribute('aria-hidden', 'false');

    if (!hasPlan) {
        modalBody.innerHTML = `
            <div class="empty-state text-center">
                <span class="empty-icon">📭</span>
                <h4>No Plan Generated</h4>
                <p>User profile exists in database, but no 7-day routine has been generated yet.</p>
            </div>
        `;
        return;
    }

    modalBody.innerHTML = `
        <div class="modal-loading text-center" style="padding: 2rem;">
            <p>Loading AI workout data for ${name}...</p>
        </div>
    `;

    // Fetch JSON from API
    fetch(`/api/user/${userId}/json`)
        .then(res => res.json())
        .then(data => {
            const plan = data.plan;
            let html = `
                <div style="margin-bottom: 1.5rem;">
                    <h4 style="color: var(--primary); font-size: 1.2rem; margin-bottom: 0.25rem;">${plan.plan_title}</h4>
                    <p style="color: var(--text-secondary); font-size: 0.95rem;">${plan.summary}</p>
                    ${data.feedback ? `<div style="margin-top: 0.75rem; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 0.5rem 0.75rem; border-radius: 0.5rem; font-size: 0.85rem; color: #fbbf24;"><strong>Feedback Applied:</strong> "${data.feedback}"</div>` : ''}
                </div>
                <div style="display: flex; flex-direction: column; gap: 1rem;">
            `;

            (plan.days || []).forEach(d => {
                html += `
                    <div style="background: rgba(0,0,0,0.3); border: 1px solid var(--border-subtle); border-radius: 0.75rem; padding: 1rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <strong style="color: #ffffff;">Day ${d.day}: ${d.title}</strong>
                            <span style="font-size: 0.8rem; color: var(--primary);">${d.focus}</span>
                        </div>
                        <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem;">Warm-up: ${d.warm_up}</div>
                        ${d.is_rest_day && (!d.exercises || d.exercises.length === 0) ? `
                            <div style="font-size: 0.85rem; color: #34d399;">🌱 Active Recovery & Rest</div>
                        ` : `
                            <ul style="list-style: none; padding-left: 0; font-size: 0.85rem;">
                                ${(d.exercises || []).map(ex => `
                                    <li style="padding: 0.25rem 0; border-bottom: 1px dashed rgba(255,255,255,0.05); display: flex; justify-content: space-between;">
                                        <span>• ${ex.name}</span>
                                        <span style="color: var(--text-muted);">${ex.sets} × ${ex.reps} (Rest: ${ex.rest})</span>
                                    </li>
                                `).join('')}
                            </ul>
                        `}
                        <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.5rem;">Cool-down: ${d.cool_down}</div>
                    </div>
                `;
            });

            html += `
                </div>
                <div style="margin-top: 1.5rem; background: rgba(0, 230, 118, 0.08); border: 1px solid var(--border-accent); padding: 1rem; border-radius: 0.75rem;">
                    <strong style="color: var(--primary); font-size: 0.9rem;">AI Nutrition Recommendation:</strong>
                    <p style="font-size: 0.9rem; color: var(--text-primary); margin-top: 0.35rem;">${plan.nutrition_tip}</p>
                </div>
            `;

            modalBody.innerHTML = html;
        })
        .catch(err => {
            modalBody.innerHTML = `
                <div class="alert alert-danger">
                    Failed to fetch plan data from API: ${err.message}
                </div>
            `;
        });
}

function closeInspectModal() {
    const modal = document.getElementById('inspectModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.setAttribute('aria-hidden', 'true');
    }
}

function confirmDeleteUser(userId, userName) {
    const modal = document.getElementById('deleteModal');
    const nameEl = document.getElementById('delUserName');
    const idEl = document.getElementById('delUserId');
    const form = document.getElementById('deleteUserForm');

    if (modal && nameEl && idEl && form) {
        nameEl.textContent = userName;
        idEl.textContent = userId;
        form.action = `/admin/delete-user/${userId}`;

        modal.classList.remove('hidden');
        modal.setAttribute('aria-hidden', 'false');
    }
}

function closeDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (modal) {
        modal.classList.add('hidden');
        modal.setAttribute('aria-hidden', 'true');
    }
}

/* ==========================================================================
   6. Smooth Scrolling
   ========================================================================== */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            if (targetId && targetId !== '#') {
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    });
}
