// Complete Dashboard JavaScript
document.addEventListener('DOMContentLoaded', function () {

    // Initialize tab switching
    const tabLinks = document.querySelectorAll('.nav-link[data-tab]');
    tabLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const tabName = this.dataset.tab;
            switchTab(tabName);
        });
    });

    // Handle Customer Form Submission via AJAX
    const customerForm = document.getElementById('customerForm');
    if (customerForm) {
        customerForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = {
                name: document.getElementById('customerName').value,
                email: document.getElementById('customerEmail').value,
                phone: document.getElementById('customerPhone').value,
                address: document.getElementById('customerAddress').value
            };

            try {
                const response = await fetch('/crm/api/new', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data.success) {
                    // Close modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('newCustomerModal'));
                    modal.hide();

                    // Show success message
                    showAlert('Customer created successfully!', 'success');

                    // Reload customer data
                    loadCustomers();

                    // Reset form
                    customerForm.reset();
                }
            } catch (error) {
                showAlert('Error creating customer: ' + error.message, 'danger');
            }
        });
    }

    // Handle Product Form Submission
    const productForm = document.getElementById('productForm');
    if (productForm) {
        productForm.addEventListener('submit', async function (e) {
            e.preventDefault();

            const formData = {
                name: document.getElementById('productName').value,
                description: document.getElementById('productDescription').value,
                price: parseFloat(document.getElementById('productPrice').value)
            };

            try {
                const response = await fetch('/products/api/new', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCsrfToken()
                    },
                    body: JSON.stringify(formData)
                });

                const data = await response.json();

                if (data.success) {
                    const modal = bootstrap.Modal.getInstance(document.getElementById('newProductModal'));
                    modal.hide();
                    showAlert('Product created successfully!', 'success');
                    loadProducts();
                    productForm.reset();
                }
            } catch (error) {
                showAlert('Error creating product: ' + error.message, 'danger');
            }
        });
    }

    // Load customers into table
    async function loadCustomers() {
        try {
            const response = await fetch('/crm/api/customers');
            const customers = await response.json();

            const tbody = document.querySelector('#customersTable tbody');
            tbody.innerHTML = '';

            customers.forEach(customer => {
                const row = `
                    <tr>
                        <td>${customer.name}</td>
                        <td>${customer.email}</td>
                        <td>${customer.phone}</td>
                        <td>Individual</td>
                        <td><span class="badge bg-primary">0</span></td>
                        <td><span class="badge bg-success">Active</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="editCustomer(${customer.id})">Edit</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteCustomer(${customer.id})">Delete</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        } catch (error) {
            console.error('Error loading customers:', error);
        }
    }

    // Load products into table
    async function loadProducts() {
        try {
            const response = await fetch('/products/api/products');
            const products = await response.json();

            const tbody = document.querySelector('#productsTable tbody');
            tbody.innerHTML = '';

            products.forEach(product => {
                const row = `
                    <tr>
                        <td>${product.name}</td>
                        <td>${product.category || 'General'}</td>
                        <td>₹${parseFloat(product.price).toFixed(2)}</td>
                        <td>-</td>
                        <td>-</td>
                        <td><span class="badge bg-success">Active</span></td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" onclick="editProduct(${product.id})">Edit</button>
                            <button class="btn btn-sm btn-outline-danger" onclick="deleteProduct(${product.id})">Delete</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        } catch (error) {
            console.error('Error loading products:', error);
        }
    }

    // Tab switching function
    function switchTab(tabName) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.style.display = 'none';
        });

        // Show selected tab
        const selectedTab = document.getElementById(tabName);
        if (selectedTab) {
            selectedTab.style.display = 'block';
        }

        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

        // Load data for the tab
        if (tabName === 'customers') {
            loadCustomers();
        } else if (tabName === 'products') {
            loadProducts();
        }
    }

    // Get CSRF token
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.content || '';
    }

    // Show alert message
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show dashboard-alert`;
        alertDiv.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-triangle'}"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.querySelector('.content-area').prepend(alertDiv);

        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }

    // Initial load
    loadCustomers();
    loadProducts();
});
