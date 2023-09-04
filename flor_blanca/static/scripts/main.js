document.addEventListener("DOMContentLoaded", () => {
  const addToCartButtons = document.querySelectorAll(".add");
  const cartItemsContainer = document.getElementById("cart-items");
  const checkoutButton = document.getElementById("checkout-button");
  let cart = [];

  addToCartButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      const productId = button.parentNode.id.replace("product-", "");
      const selectedOption = document.getElementById(
        `product-${productId}-select`
      );
      const selectedQuantity = document.getElementById(`quantity-${productId}`);

      const cartItem = {
        price_id: selectedOption.value,
        quantity: selectedQuantity.value,
        name: selectedOption.options[selectedOption.selectedIndex].getAttribute(
          "data-name"
        ),
        image:
          selectedOption.options[selectedOption.selectedIndex].getAttribute(
            "data-image"
          ),
      };

      // Check if the cart item already exists
      const existingCartItemIndex = cart.findIndex(
        (item) => item.price_id === cartItem.price_id
      );

      if (existingCartItemIndex > -1) {
        // Update the quantity if the cart item already exists
        cart[existingCartItemIndex].quantity =
          parseInt(cart[existingCartItemIndex].quantity) +
          parseInt(cartItem.quantity);
      } else {
        // Add the cart item to the cart
        cart.push(cartItem);
      }
      // Store the cart items in local storage
      localStorage.setItem("cart", JSON.stringify(cart));

      // Store the cart item in your cart array or perform further actions
      console.log(cartItem);
      console.log(cart);

      displayCartItems();
      // displayTotalAmount();
    });
  });

  function displayCartItems() {
    // Clear the existing cart items
    if (cartItemsContainer) {
      cartItemsContainer.innerHTML = "";
      const storedCart = JSON.parse(localStorage.getItem("cart") || "[]");
      cart = storedCart || [];
      let totalCount = 0;

      // Add each cart item to the cart items container
      cart.forEach((cartItem, index) => {
        const cartItemElement = document.createElement("div");
        cartItemElement.classList.add("col-12", "align-items-center");
        const selectedOption = document.querySelector(
          `option[value='${cartItem.price_id}']`
        );

        // Retrieve the price from the data-price attribute
        const price = parseFloat(selectedOption.getAttribute("data-price"));

        // Calculate the total per item
        const total = (price * cartItem.quantity) / 100;
        totalCount += parseInt(cartItem.quantity);
        // Create the HTML elements to display the item details
        // <p>Price: £${price.toFixed(2)}</p>
        cartItemElement.innerHTML = `
      
      <div class="row text-center">
      <div class="col-3 ">
        <img src="${
          cartItem.image
        }" alt="Product Image" style="width: 60px; height:60px;" class="rounded rounded-2  ">
        <button class="decrease btn btn-sm mt-2" data-index="${index}">-</button>
        <button class="increase btn btn-sm mt-2" data-index="${index}">+</button>
      </div>
      <div class="col-3">
        <p><span class="fw-bold">Producto: </span>${cartItem.name}</p>
      </div>
      <div class="col-3">
        <p><span class="fw-bold">Cantidad: </span>${cartItem.quantity}</p>
      </div>
      <div class="col-2">
        <p><span class="fw-bold">Total: </span> £${total.toFixed(2)}</p>
        <button class="delete btn btn-sm" data-index="${index}"><i class="bi bi-trash"></i></button>
      </div>
     
    </div>
  
    <hr class="title border-3 w-100">
     
      `;
        cartItemsContainer.appendChild(cartItemElement);
      });

      const itemCountElement = document.querySelector(".itemCount");
      if (itemCountElement) itemCountElement.textContent = totalCount;

      const deleteButtons = document.querySelectorAll(".delete");
      deleteButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
          const index = event.target.getAttribute("data-index");
          cart.splice(index, 1);
          localStorage.setItem("cart", JSON.stringify(cart));
          displayCartItems();
        });
      });

      const decreaseButtons = document.querySelectorAll(".decrease");
      decreaseButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
          const index = event.target.getAttribute("data-index");
          if (cart[index].quantity > 1) {
            cart[index].quantity--;
            localStorage.setItem("cart", JSON.stringify(cart));
            displayCartItems();
          }
        });
      });

      const increaseButtons = document.querySelectorAll(".increase");
      increaseButtons.forEach((button) => {
        button.addEventListener("click", (event) => {
          const index = event.target.getAttribute("data-index");
          cart[index].quantity++;
          localStorage.setItem("cart", JSON.stringify(cart));
          displayCartItems();
        });
      });
    }
  }
  // const totalSpan = document.getElementById("total");
  // let displayTotalAmount = () => {
  //   cart.forEach((cartItem) => {
  //     let total = 0;
  //     let result =
  //       (parseInt(cartItem.quantity) * parseInt(cartItem.price)) / 100;
  //     console.log(cartItem.price);

  //     total += result;

  //     totalSpan.innerHTML = total;
  //   });
  // };

  if (checkoutButton) {
    checkoutButton.addEventListener("click", () => {
      if (cart.length > 0) {
        fetch("/shop_checkout", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(cart),
        })
          .then((response) => response.json())
          .then((data) => {
            // Redirect to the success_url
            window.location.href = data;
          })
          .catch((error) => {
            console.error("Error:", error);
          });
      }
    });
  }
  displayCartItems();
});
