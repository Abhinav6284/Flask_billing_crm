document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mainContent = document.getElementById('mainContent');

    // --- Sidebar and Mobile Menu ---
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.toggle('collapsed');
            mainContent.classList.toggle('collapsed');
        });
    }

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }

    // --- Tab Switching ---
    const tabLinks = document.querySelectorAll('.nav-link[data-tab]');
    const pageTitle = document.getElementById('pageTitle');
    const breadcrumb = document.getElementById('breadcrumb');

    function switchTab(tabId) {
        document.querySelectorAll('.tab-content').forEach(tab => tab.style.display = 'none');
        document.getElementById(tabId).style.display = 'block';

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

    // Also handle tab switching from view-all buttons
    document.querySelectorAll('.view-all-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const tabId = e.currentTarget.getAttribute('data-tab');
            switchTab(tabId);
        });
    });


    // --- AJAX Form Submissions ---
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Customer Form
    const customerForm = document.getElementById('customerForm');
    if (customerForm) {
        customerForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());

            fetch("{{ url_for('crm.api_new_customer') }}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('newCustomerModal'));
                        modal.hide();
                        location.reload(); // Reload to see changes
                    } else {
                        alert('Error: ' + (result.message || 'Could not add customer.'));
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    }

    // Product Form
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = Object.fromEntries(formData.entries());

            fetch("{{ url_for('products.api_new_product') }}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('newProductModal'));
                        modal.hide();
                        location.reload(); // Reload to see changes
                    } else {
                        alert('Error: ' + (result.message || 'Could not add product.'));
                    }
                })
                .catch(error => console.error('Error:', error));
        });
    }

    switchTab('dashboard');
});