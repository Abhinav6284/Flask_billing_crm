document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');

    // --- Sidebar and Mobile Menu ---
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => sidebar.classList.toggle('collapsed'));
    }
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => sidebar.classList.toggle('show'));
    }

    // --- Tab Switching ---
    const tabLinks = document.querySelectorAll('.nav-link[data-tab]');
    const pageTitle = document.getElementById('pageTitle');
    const breadcrumb = document.getElementById('breadcrumb');

    window.switchTab = function (tabId) { // Make it globally accessible for buttons
        document.querySelectorAll('.tab-content').forEach(tab => {
            if (tab) tab.style.display = 'none';
        });
        const selectedTab = document.getElementById(tabId);
        if (selectedTab) selectedTab.style.display = 'block';

        tabLinks.forEach(link => link.classList.remove('active'));
        const activeLink = document.querySelector(`.nav-link[data-tab="${tabId}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
            const tabTitle = activeLink.querySelector('.nav-text').textContent;
            pageTitle.textContent = tabTitle;
            breadcrumb.textContent = `Home / ${tabTitle}`;
        }
    }

    // --- Handle Hash Change for Tab Switching ---
    function handleHashChange() {
        const hash = window.location.hash.substring(1); // Get tab ID from URL hash
        if (hash) {
            switchTab(hash);
        } else {
            switchTab('dashboard'); // Default to dashboard if no hash
        }
    }

    window.addEventListener('hashchange', handleHashChange);
    tabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            // Let the default link behavior (changing the hash) trigger the 'hashchange' event
        });
    });

    document.querySelectorAll('.view-all-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = e.currentTarget.getAttribute('data-tab');
            window.location.hash = tabId;
        });
    });

    // --- AJAX Form Submissions ---
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    document.getElementById('customerForm')?.addEventListener('submit', function (e) {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(this).entries());
        fetch('/customers/api/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify(data)
        }).then(res => res.json()).then(result => {
            if (result.success) location.reload();
            else alert('Error: ' + (result.message || 'Could not add customer.'));
        });
    });

    document.getElementById('productForm')?.addEventListener('submit', function (e) {
        e.preventDefault();
        const data = Object.fromEntries(new FormData(this).entries());
        fetch('/products/api/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
            body: JSON.stringify(data)
        }).then(res => res.json()).then(result => {
            if (result.success) location.reload();
            else alert('Error: ' + (result.message || 'Could not add product.'));
        });
    });

    // --- NEW: DELETE FUNCTIONALITY ---
    document.body.addEventListener('click', function (e) {
        const target = e.target.closest('button'); // Ensure we get the button if an icon inside it is clicked
        if (!target) return;

        // Delete Customer
        if (target.matches('.delete-customer-btn')) {
            const customerId = target.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this customer? This cannot be undone.')) {
                fetch(`/customers/api/${customerId}/delete`, {
                    method: 'DELETE',
                    headers: { 'X-CSRFToken': csrfToken }
                })
                    .then(res => res.json())
                    .then(result => {
                        if (result.success) {
                            location.reload(); // Reload the page to show updated list
                        } else {
                            alert('Error: ' + (result.message || 'Could not delete customer.'));
                        }
                    });
            }
        }

        // Delete Product
        if (target.matches('.delete-product-btn')) {
            const productId = target.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this product? This cannot be undone.')) {
                fetch(`/products/api/${productId}/delete`, {
                    method: 'DELETE',
                    headers: { 'X-CSRFToken': csrfToken }
                })
                    .then(res => res.json())
                    .then(result => {
                        if (result.success) {
                            location.reload(); // Reload the page to show updated list
                        } else {
                            alert('Error: ' + (result.message || 'Could not delete product.'));
                        }
                    });
            }
        }
    });

    // --- TABLE POPULATION FUNCTIONS (UPDATED WITH DELETE BUTTONS) ---
    function populateTables(data) {
        const { customers, products, invoices } = data;

        const cTbody = document.getElementById('customersTableBody');
        if (cTbody) {
            cTbody.innerHTML = customers.length > 0 ? customers.map(c => `
                <tr>
                    <td>${c.name}</td><td>${c.email}</td><td>${c.phone}</td>
                    <td>${c.customer_type}</td><td><span class="badge bg-primary">0</span></td>
                    <td><span class="badge bg-success">${c.status}</span></td>
                    <td>
                        <a href="/customers/${c.id}/edit" class="btn btn-sm btn-outline-primary">Edit</a>
                        <button class="btn btn-sm btn-outline-danger delete-customer-btn" data-id="${c.id}">Delete</button>
                    </td>
                </tr>`).join('') : '<tr><td colspan="7" class="text-center">No customers found.</td></tr>';
        }

        const pTbody = document.getElementById('productsTableBody');
        if (pTbody) {
            pTbody.innerHTML = products.length > 0 ? products.map(p => `
                <tr>
                    <td>${p.name}</td><td>${p.category || 'N/A'}</td><td>₹${p.price.toFixed(2)}</td>
                    <td>${p.stock_quantity ?? '-'}</td><td>${p.sku || '-'}</td>
                    <td><span class="badge bg-success">${p.status}</span></td>
                    <td>
                        <a href="/products/${p.id}/edit" class="btn btn-sm btn-outline-primary">Edit</a>
                        <button class="btn btn-sm btn-outline-danger delete-product-btn" data-id="${p.id}">Delete</button>
                    </td>
                </tr>`).join('') : '<tr><td colspan="7" class="text-center">No products found.</td></tr>';
        }

        // (Invoice table remains the same as it doesn't have a delete button in this flow)
        const iTbody = document.getElementById('invoicesTableBody');
        if (iTbody) {
            iTbody.innerHTML = invoices.length > 0 ? invoices.map(i => {
                const statusClass = { 'Paid': 'bg-success', 'Unpaid': 'bg-warning', 'Overdue': 'bg-danger' }[i.status] || 'bg-secondary';
                return `
                    <tr>
                        <td><a href="/invoices/${i.id}">${i.invoice_number}</a></td><td>${i.customer}</td>
                        <td>${i.date_issued}</td><td>${i.due_date}</td><td>₹${i.total.toFixed(2)}</td>
                        <td><span class="badge ${statusClass}">${i.status}</span></td>
                        <td><a href="/invoices/${i.id}" class="btn btn-sm btn-outline-info">View</a></td>
                    </tr>`;
            }).join('') : '<tr><td colspan="7" class="text-center">No invoices found.</td></tr>';
        }
    }

    // --- CHARTING & REPORTS LOGIC (Unchanged) ---
    let mainRevenueChart, mainCategoryChart, salesChart, customerGrowthChart, revenueTrendsChart;
    function destroyCharts() { /* ... */ }
    function renderMainCharts(data) { /* ... */ }
    function renderReportCharts(reportData) { /* ... */ }
    // ... (rest of the chart and report functions remain the same)

    // --- INITIALIZE DASHBOARD ---
    function initializeDashboard() {
        fetch('/api/dashboard_data')
            .then(response => response.json())
            .then(data => {
                populateTables(data);
                // renderMainCharts(data); // This line can be uncommented if you want charts on the main dashboard
            });

        handleHashChange();
        // setDateRange(); // This line can be uncommented if you want to set the date range on load
    }

    initializeDashboard();
});