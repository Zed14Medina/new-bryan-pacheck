// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Placeholder function to update the cart UI (e.g., cart count, total)
function updateCartUI(cartTotal, cartCount) {
    console.log(`Cart updated: Total - ${cartTotal}, Count - ${cartCount}`);
    // You can add code here later to update the actual HTML elements
    const cartCountElement = document.getElementById('cart-count');
    if (cartCountElement) {
        cartCountElement.innerText = cartCount;
    }
}

// Placeholder function to show notifications to the user
function showNotification(message, type = 'success') {
    console.log(`Notification (${type}): ${message}`);
    // You can add code here later to display a visible notification (e.g., using a modal or a toast)
}

window.switchRole = function() {
  const currentPath = window.location.pathname;
  if (currentPath.includes('buyer') || currentPath === '/') {
    window.location.href = '/seller/';
  } else if (currentPath.includes('seller')) {
    window.location.href = '/buyer/';
  } else {
    window.location.href = '/buyer/';
  }
};

// Function to open the sidebar
function openMenu() {
  const sideMenu = document.getElementById("sideMenu");
  if (sideMenu) {
    sideMenu.style.width = "280px"; // Increased width for better visibility
    sideMenu.style.boxShadow = "2px 0 5px rgba(0, 0, 0, 0.2)"; // Added shadow for depth
  }
}

// Function to close the sidebar
function closeMenu() {
  const sideMenu = document.getElementById("sideMenu");
  if (sideMenu) {
    sideMenu.style.width = "0";
    sideMenu.style.boxShadow = "none";
  }
}


// Add event listener to "Change Role" links after DOM is ready
window.addEventListener('load', () => {
  // Wire the "Change Role" links
  document.querySelectorAll('a.change-role').forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      window.switchRole();
    });
  });

  // Populate username
  const name = localStorage.getItem("username");
  if (name) {
    document.querySelectorAll("#userName").forEach(el => el.innerText = name);
  }

  // Wire dropdown filter if present
  const cat = document.getElementById('category-filter');
  if (cat) {
    cat.addEventListener('change', filterProducts);
    filterProducts();
  }
});

// ------------------------ CLICKING PRODUCT --------------------------- //
function viewProduct(productName) {
  alert("You clicked on " + productName);
}

// ------------------------ EDIT --------------------------- //
const editForm = document.getElementById('editForm');
if (editForm) {
  let currentProductId = null;

  editForm.addEventListener('submit', function(event) {
    event.preventDefault();

    const productName = document.getElementById('product-name').value;
    let productPrice = document.getElementById('product-price').value;

    if (!productPrice.includes('.')) {
      productPrice += '.00';
    }

    if (currentProductId) {
      document.getElementById(`product-name-${currentProductId}`).innerText = productName;
      document.getElementById(`product-price-${currentProductId}`).innerText =
        `Php ${parseFloat(productPrice).toFixed(2)}`;
    }

    const editModal = document.getElementById('editModal') || document.getElementById('editProductModal');
    if (editModal) editModal.style.display = 'none';
  });
}

// ------------------------ IMAGE --------------------------- //
function previewImage(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const preview = document.getElementById('image-preview');
    const container = document.getElementById('image-preview-container');
    if (preview && container) {
      preview.src = e.target.result;
      container.style.display = 'block';
      container.style.marginTop = '15px'; // Added spacing
    }
  };
  reader.readAsDataURL(file);
}

// ------------------------ ADD PRODUCT --------------------------- //
let isAdding = false;
function openAddProductModal() {
  const modal = document.getElementById('addProductModal');
  if (modal) {
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
  }
}

function closeAddProductModal() {
  const modal = document.getElementById('addProductModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = ''; // Restore scrolling
  }
}

function openEditProductModal(productName, productPrice, productId) {
  const modal = document.getElementById('editProductModal');
  if (modal) {
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden';
    
    // Set the product details for editing
    const nameInput = document.getElementById('product-name');
    const priceInput = document.getElementById('product-price');
    if (nameInput) nameInput.value = productName;
    if (priceInput) priceInput.value = productPrice;
    
    // Store the current product ID
    window.currentProductId = productId;
  }
}

function closeEditProductModal() {
  const modal = document.getElementById('editProductModal');
  if (modal) {
    modal.style.display = 'none';
    document.body.style.overflow = '';
  }
}

// ------------------------ BUYER PAGE --------------------------- //
function addToCart(productId, quantity = 1) {
    fetch('/update-cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity,
            action: 'add'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateCartUI(data.cart_total, data.cart_count);
            showNotification('Product added to cart successfully!');
        } else {
            showNotification('Error adding product to cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error adding product to cart', 'error');
    });
}

function updateCartItem(productId, quantity) {
    fetch('/update-cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            quantity: quantity,
            action: 'update'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateCartUI(data.cart_total, data.cart_count);
            showNotification('Cart updated successfully!');
        } else {
            showNotification('Error updating cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error updating cart', 'error');
    });
}

function removeFromCart(productId) {
    fetch('/update-cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            product_id: productId,
            action: 'remove'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateCartUI(data.cart_total, data.cart_count);
            const cartItem = document.querySelector(`[data-product-id="${productId}"]`);
            if (cartItem) {
                cartItem.remove();
            }
            showNotification('Product removed from cart');
        } else {
            showNotification('Error removing product from cart', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error removing product from cart', 'error');
    });
}

function checkoutProduct(productId) {
  window.location.href = `/checkout/${productId}/`;
}

function searchProducts(query) {
    window.location.href = `/search/?q=${encodeURIComponent(query)}`;
}

function filterProducts() {
    const category = document.getElementById('category-filter').value;
    const minPrice = document.getElementById('min-price').value;
    const maxPrice = document.getElementById('max-price').value;
    
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);
    
    window.location.href = `/filter/?${params.toString()}`;
}

// ------------------------ DROPDOWNS --------------------------- //
function filterByPrice() {
  const [min, max] = document.getElementById('price-range').value.split('-').map(Number);
  const products = document.querySelectorAll('.product');
  
  products.forEach(product => {
    const price = Number(product.dataset.price);
    const shouldShow = price >= min && price <= max;
    product.style.display = shouldShow ? 'block' : 'none';
    
    // Add transition effect
    if (shouldShow) {
      product.style.opacity = '0';
      setTimeout(() => {
        product.style.opacity = '1';
      }, 50);
    }
  });
}

function filterByCategory() {
  const category = document.getElementById('category-filter').value;
  const products = document.querySelectorAll('.product');
  
  products.forEach(product => {
    const productCategory = product.dataset.category;
    const shouldShow = category === 'all' || category === productCategory;
    product.style.display = shouldShow ? 'block' : 'none';
    
    // Add transition effect
    if (shouldShow) {
      product.style.opacity = '0';
      setTimeout(() => {
        product.style.opacity = '1';
      }, 50);
    }
  });
}

// ------------------------ CART --------------------------- //
let productToRemove;
function increaseQuantity(id) {
  const fld = document.getElementById('quantity-'+id);
  if (fld) fld.value = parseInt(fld.value)+1;
}
function decreaseQuantity(id) {
  const fld = document.getElementById('quantity-'+id);
  if (fld && parseInt(fld.value)>1) fld.value = parseInt(fld.value)-1;
}
function openRemoveModal(id) {
  productToRemove = id;
  const m = document.getElementById('removeModal');
  if (m) m.style.display = 'block';
}
function closeRemoveModal() {
  const m = document.getElementById('removeModal');
  if (m) m.style.display = 'none';
}
function removeProduct() {
  const el = document.getElementById('product-'+productToRemove);
  if (el) el.remove();

  let cart = JSON.parse(localStorage.getItem('cartData')||'[]');
  cart = cart.filter(item=>item.id!==productToRemove);
  localStorage.setItem('cartData', JSON.stringify(cart));

  if (cart.length===0) {
    const c = document.getElementById('cart-items');
    if (c) c.innerHTML = "<div class='empty-cart-message'>Your cart is empty!</div>";
  }
  closeRemoveModal();
}
function saveCartAndProceed() {
  const cart = [
    {id:1, name:'Product 1', quantity:document.getElementById('quantity-1').value, price:30.00},
    {id:2, name:'Product 2', quantity:document.getElementById('quantity-2').value, price:20.00}
  ];
  localStorage.setItem('cartData', JSON.stringify(cart));
  window.location.href = '/checkout';
}

// ------------------------ CHECKOUT --------------------------- //
function selectPaymentMethod(method) {
  alert('You selected ' + method + ' as the payment method. It has been noted.');
}
