// ── Modal helpers ────────────────────────────────────────
function openModal(id) {
    document.getElementById(id).classList.add('open');
}
function closeModal(id) {
    document.getElementById(id).classList.remove('open');
    // Clear errors
    const err = document.getElementById(id.replace('Modal', '') + '-error');
    if (err) err.textContent = '';
}

// Close modal on overlay click
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', function(e) {
        if (e.target === this) closeModal(this.id);
    });
});

// Open add modal
document.getElementById('openAddModal').addEventListener('click', () => {
    // Set today's date as default
    document.getElementById('add-date').value = new Date().toISOString().split('T')[0];
    document.getElementById('add-amount').value = '';
    document.getElementById('add-description').value = '';
    document.getElementById('add-type').value = 'Income';
    document.getElementById('add-category').value = 'Salary';
    document.getElementById('add-error').textContent = '';
    openModal('addModal');
});

// ── CSRF helper ──────────────────────────────────────────
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let c of cookies) {
            c = c.trim();
            if (c.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(c.slice(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ── Toast ────────────────────────────────────────────────
function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

// ── Add Transaction ──────────────────────────────────────
async function submitAdd() {
    const type     = document.getElementById('add-type').value;
    const category = document.getElementById('add-category').value;
    const amount   = document.getElementById('add-amount').value;
    const date     = document.getElementById('add-date').value;
    const desc     = document.getElementById('add-description').value;
    const errEl    = document.getElementById('add-error');

    if (!amount || parseFloat(amount) <= 0) {
        errEl.textContent = 'Amount must be greater than 0.';
        return;
    }
    if (!date) {
        errEl.textContent = 'Please select a date.';
        return;
    }

    try {
        const res = await fetch('/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ transaction_type: type, category, amount: parseFloat(amount), date, description: desc }),
        });
        const data = await res.json();
        if (data.success) {
            closeModal('addModal');
            showToast('✅ Transaction saved successfully');
            setTimeout(() => location.reload(), 800);
        } else {
            errEl.textContent = data.error || 'Failed to save transaction.';
        }
    } catch (e) {
        errEl.textContent = 'Network error. Please try again.';
    }
}

// ── Edit Transaction ─────────────────────────────────────
async function openEditModal(id) {
    try {
        const res = await fetch(`/get/${id}/`);
        const data = await res.json();
        if (!data.success) { showToast('❌ Could not load transaction.'); return; }

        document.getElementById('edit-id').value          = data.id;
        document.getElementById('edit-type').value        = data.transaction_type;
        document.getElementById('edit-category').value    = data.category;
        document.getElementById('edit-amount').value      = data.amount;
        document.getElementById('edit-date').value        = data.date;
        document.getElementById('edit-description').value = data.description;
        document.getElementById('edit-error').textContent = '';
        openModal('editModal');
    } catch (e) {
        showToast('❌ Network error.');
    }
}

async function submitEdit() {
    const id       = document.getElementById('edit-id').value;
    const type     = document.getElementById('edit-type').value;
    const category = document.getElementById('edit-category').value;
    const amount   = document.getElementById('edit-amount').value;
    const date     = document.getElementById('edit-date').value;
    const desc     = document.getElementById('edit-description').value;
    const errEl    = document.getElementById('edit-error');

    if (!amount || parseFloat(amount) <= 0) {
        errEl.textContent = 'Amount must be greater than 0.';
        return;
    }

    try {
        const res = await fetch(`/edit/${id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ transaction_type: type, category, amount: parseFloat(amount), date, description: desc }),
        });
        const data = await res.json();
        if (data.success) {
            closeModal('editModal');
            showToast('✅ Transaction updated successfully');
            setTimeout(() => location.reload(), 800);
        } else {
            errEl.textContent = data.error || 'Failed to update.';
        }
    } catch (e) {
        errEl.textContent = 'Network error. Please try again.';
    }
}

// ── Delete Transaction ───────────────────────────────────
function openDeleteModal(id) {
    document.getElementById('delete-id').value = id;
    openModal('deleteModal');
}

async function submitDelete() {
    const id = document.getElementById('delete-id').value;
    try {
        const res = await fetch(`/delete/${id}/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
        });
        const data = await res.json();
        if (data.success) {
            closeModal('deleteModal');
            showToast('🗑️ Transaction deleted');
            setTimeout(() => location.reload(), 800);
        } else {
            showToast('❌ Could not delete transaction.');
        }
    } catch (e) {
        showToast('❌ Network error.');
    }
}