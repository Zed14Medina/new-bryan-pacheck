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
  document.getElementById("sideMenu").style.width = "250px";
}

// Function to close the sidebar
function closeMenu() {
  document.getElementById("sideMenu").style.width = "0";
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
    }
  };
  reader.readAsDataURL(file);
}

// ------------------------ ADD PRODUCT --------------------------- //
let isAdding = false;
function openAddModal() {
  isAdding = true;
  window.currentProductId = null;

  const modal = document.getElementById('addProductModal') || document.getElementById('editModal');
  if (modal) modal.style.display = 'block';

  const nameFld = document.getElementById('product-name');
  const priceFld = document.getElementById('product-price');
  const imageFld = document.getElementById('product-image');
  const imgPreview = document.getElementById('image-preview-container');
  if (nameFld) nameFld.value = '';
  if (priceFld) priceFld.value = '';
  if (imageFld) imageFld.value = '';
  if (imgPreview) imgPreview.style.display = 'none';

  if (nameFld) nameFld.placeholder = 'Enter product name';
  if (priceFld) priceFld.placeholder = 'Enter product price';
}

// ------------------------ BUYER PAGE --------------------------- //
function addToCart(productId) {
  alert(`Added ${productId} to cart.`);
}
function checkoutProduct(productId) {
  window.location.href = `/checkout/${productId}/`;
}
function searchProducts(event) {
  event.preventDefault();
  const q = document.getElementById('searchInput').value.trim();
  if (q) {
    window.location.href = `/search/?q=${encodeURIComponent(q)}`;
  }
  return false;
}

// ------------------------ DROPDOWNS --------------------------- //
function filterByPrice() {
  const [min, max] = document.getElementById('price-range').value
    .split('-').map(Number);
  document.querySelectorAll('.product').forEach(p => {
    const price = Number(p.dataset.price);
    p.style.display = (price>=min && price<=max) ? 'block' : 'none';
  });
}

function filterProducts() {
  const val = document.getElementById('category-filter').value;
  document.querySelectorAll('.product').forEach(p => {
    const cat = p.dataset.category;
    p.style.display = (val==='all' || val===cat) ? 'block' : 'none';
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
