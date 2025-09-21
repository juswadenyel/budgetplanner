let totalBudget = 0;
let totalExpenses = 0;

const form = document.getElementById('budget-form');
const itemInput = document.getElementById('item');
const amountInput = document.getElementById('amount');
const expenseList = document.getElementById('expense-list');
const totalBudgetEl = document.getElementById('total-budget');
const totalExpensesEl = document.getElementById('total-expenses');
const remainingEl = document.getElementById('remaining');

form.addEventListener('submit', function(e) {
    e.preventDefault();

    const item = itemInput.value;
    const amount = parseFloat(amountInput.value);

    if (!item || isNaN(amount) || amount <= 0) return;

    totalExpenses += amount;
    totalBudget += amount; // If you want a total budget, you can adjust
    updateSummary();

    const li = document.createElement('li');
    li.innerHTML = `${item} - $${amount.toFixed(2)} <button class="delete-btn">Delete</button>`;
    expenseList.appendChild(li);

    li.querySelector('.delete-btn').addEventListener('click', () => {
        totalExpenses -= amount;
        li.remove();
        updateSummary();
    });

    itemInput.value = '';
    amountInput.value = '';
});

function updateSummary() {
    totalExpensesEl.textContent = totalExpenses.toFixed(2);
    totalBudgetEl.textContent = totalBudget.toFixed(2);
    remainingEl.textContent = (totalBudget - totalExpenses).toFixed(2);
}
