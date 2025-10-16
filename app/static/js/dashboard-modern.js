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

    tabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = e.currentTarget.getAttribute('data-tab');
            switchTab(tabId);
        });
    });

    document.querySelectorAll('.view-all-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = e.currentTarget.getAttribute('data-tab');
            switchTab(tabId);
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
            else alert('Error: Could not add customer.');
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
            else alert('Error: Could not add product.');
        });
    });

    // --- TABLE POPULATION FUNCTIONS ---
    function populateCustomersTable(customers) {
        const tableBody = document.getElementById('customersTableBody');
        if (!tableBody) return;
        tableBody.innerHTML = '';
        if (customers.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No customers found.</td></tr>';
            return;
        }
        customers.forEach(c => {
            const row = `
                <tr>
                    <td>${c.name}</td>
                    <td>${c.email}</td>
                    <td>${c.phone}</td>
                    <td>${c.customer_type}</td>
                    <td><span class="badge bg-primary">0</span></td>
                    <td><span class="badge bg-success">${c.status}</span></td>
                    <td>
                        <a href="/customers/${c.id}/edit" class="btn btn-sm btn-outline-primary">Edit</a>
                    </td>
                </tr>
            `;
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    }

    function populateProductsTable(products) {
        const tableBody = document.getElementById('productsTableBody');
        if (!tableBody) return;
        tableBody.innerHTML = '';
        if (products.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No products found.</td></tr>';
            return;
        }
        products.forEach(p => {
            const row = `
                <tr>
                    <td>${p.name}</td>
                    <td>${p.category || 'N/A'}</td>
                    <td>₹${p.price.toFixed(2)}</td>
                    <td>${p.stock_quantity !== null ? p.stock_quantity : '-'}</td>
                    <td>${p.sku || '-'}</td>
                    <td><span class="badge bg-success">${p.status}</span></td>
                    <td>
                         <a href="/products/${p.id}/edit" class="btn btn-sm btn-outline-primary">Edit</a>
                    </td>
                </tr>
            `;
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    }

    function populateInvoicesTable(invoices) {
        const tableBody = document.getElementById('invoicesTableBody');
        if (!tableBody) return;
        tableBody.innerHTML = '';
        if (invoices.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" class="text-center">No invoices found.</td></tr>';
            return;
        }
        invoices.forEach(i => {
            const statusClass = { 'Paid': 'bg-success', 'Unpaid': 'bg-warning', 'Overdue': 'bg-danger' }[i.status] || 'bg-secondary';
            const row = `
                <tr>
                    <td><a href="/invoices/${i.id}">${i.invoice_number}</a></td>
                    <td>${i.customer}</td>
                    <td>${i.date_issued}</td>
                    <td>${i.due_date}</td>
                    <td>₹${i.total.toFixed(2)}</td>
                    <td><span class="badge ${statusClass}">${i.status}</span></td>
                    <td>
                        <a href="/invoices/${i.id}" class="btn btn-sm btn-outline-info">View</a>
                    </td>
                </tr>
            `;
            tableBody.insertAdjacentHTML('beforeend', row);
        });
    }


    // --- CHARTING LOGIC ---
    function renderCharts(data) {
        // 1. Revenue Analytics Chart (Line)
        const revenueCtx = document.getElementById('revenueChart')?.getContext('2d');
        if (revenueCtx && data.invoices && data.invoices.length > 0) {
            const monthlyRevenue = {};
            data.invoices.forEach(invoice => {
                const month = new Date(invoice.date_issued).toLocaleString('default', { month: 'short', year: 'numeric' });
                if (!monthlyRevenue[month]) {
                    monthlyRevenue[month] = 0;
                }
                monthlyRevenue[month] += invoice.total;
            });

            const sortedLabels = Object.keys(monthlyRevenue).sort((a, b) => new Date(a) - new Date(b));
            const sortedData = sortedLabels.map(label => monthlyRevenue[label]);

            new Chart(revenueCtx, {
                type: 'line',
                data: {
                    labels: sortedLabels,
                    datasets: [{
                        label: 'Monthly Revenue',
                        data: sortedData,
                        backgroundColor: 'rgba(212, 175, 55, 0.2)',
                        borderColor: 'rgba(212, 175, 55, 1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true
                    }]
                }
            });
        }

        // 2. Sales by Category Chart (Pie)
        const categoryCtx = document.getElementById('categoriesChart')?.getContext('2d');
        if (categoryCtx && data.products && data.products.length > 0) {
            const categoryCounts = {};
            data.products.forEach(product => {
                const category = product.category || 'General';
                categoryCounts[category] = (categoryCounts[category] || 0) + 1;
            });

            new Chart(categoryCtx, {
                type: 'doughnut',
                data: {
                    labels: Object.keys(categoryCounts),
                    datasets: [{
                        label: 'Products by Category',
                        data: Object.values(categoryCounts),
                        backgroundColor: [
                            '#D4AF37', '#36A2EB', '#FF6384', '#4BC0C0', '#9966FF', '#FF9F40'
                        ],
                        hoverOffset: 4
                    }]
                }
            });
        }
    }

    // --- FETCH DATA AND INITIALIZE DASHBOARD ---
    function initializeDashboard() {
        fetch('/api/dashboard_data')
            .then(response => response.json())
            .then(data => {
                console.log("Dashboard data fetched:", data); // For debugging
                renderCharts(data); // Call charting function
                populateCustomersTable(data.customers);
                populateProductsTable(data.products);
                populateInvoicesTable(data.invoices);
            })
            .catch(error => console.error('Error fetching dashboard data:', error));

        switchTab('dashboard'); // Set initial tab
    }

    // Run Initialization
    initializeDashboard();
});