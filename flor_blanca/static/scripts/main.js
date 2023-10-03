document.addEventListener("DOMContentLoaded", () => {
  const addToCartButtons = document.querySelectorAll(".add");
  const cartItemsContainer = document.getElementById("cart-items");
  const checkoutButton = document.getElementById("checkout-button");
  const totalSpan = document.getElementById("total");
  let cart = [];

  addToCartButtons.forEach((button) => {
    button.addEventListener("click", (event) => {
      event.preventDefault();

      const quantityInput = button.parentNode.querySelector(".item");
      let quantity = parseInt(quantityInput.value);

      if (!quantity || quantity < 1) {
        quantity = 1; // Set quantity as 1 if it is less than 1
        quantityInput.value = quantity;
      }

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
      const existingCartItem = cart.find(
        (item) => item.price_id === cartItem.price_id
      );

      if (existingCartItem) {
        // Update the quantity if the cart item already exists
        existingCartItem.quantity =
          parseInt(existingCartItem.quantity) + parseInt(cartItem.quantity);
      } else {
        cart.push(cartItem);
      }
      // Store the cart items in local storage
      localStorage.setItem("cart", JSON.stringify(cart));

      displayCartItems();
      showToast();
    });
  });

  function showToast() {
    const toast = document.getElementById("toast");
    toast.classList.remove("hide");
    setTimeout(function () {
      toast.classList.add("hide");
    }, 2000);
  }

  function displayCartItems() {
    // Clear the existing cart items
    if (cartItemsContainer) {
      cartItemsContainer.innerHTML = "";
      const storedCart = JSON.parse(localStorage.getItem("cart") || "[]");
      cart = storedCart || [];
      let totalCount = 0;
      let totalAmount = 0;
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
        totalAmount += total;
        totalCount += parseInt(cartItem.quantity);

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

      totalSpan.innerHTML = totalAmount.toFixed(2);

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

  if (checkoutButton) {
    checkoutButton.addEventListener("click", async () => {
      if (cart.length > 0) {
        try {
          const response = await fetch("/shop_checkout", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(cart),
          });

          if (response.ok) {
            const data = await response.json();
            // Redirect to the success_url
            window.location.href = data;

            localStorage.removeItem("cart");
            // Clear the cart array
            cart = [];
          } else {
            throw new Error("Error occurred during checkout");
          }
        } catch (error) {
          console.error("Error:", error);
        }
      }
    });
  }

  displayCartItems();
});

document.addEventListener("DOMContentLoaded", function () {
  const ratePost = [...document.getElementsByClassName("ratePost")];

  const executeRating = (suns, form) => {
    const sunClassActive = "bi bi-sun-fill";
    const sunClassInactive = "bi bi-sun";

    ratePost.map((btn) => {
      btn.onclick = (e) => {
        const ratingElement = e.target.nextSibling.nextSibling;
        ratingElement.classList.toggle("d-none");
      };
    });

    suns.map((sun) => {
      sun.onclick = () => {
        let i = suns.indexOf(sun);
        const resultInput =
          sun.parentNode.parentNode.lastChild.previousElementSibling
            .previousElementSibling;
        if (sun.className === sunClassInactive) {
          for (i; i >= 0; --i) suns[i].className = sunClassActive;
          const rating = sun.parentNode.previousElementSibling.value;
          resultInput.value = rating;
        } else {
          for (i; i < suns.length; ++i) suns[i].className = sunClassInactive;
          let rating = sun.parentNode.previousElementSibling.value - 1;
          if (rating === 0) rating += 1;
          resultInput.value = rating;
        }
      };
    });
  };

  // Iterate over each form element and execute the rating logic separately for each form
  const forms = document.getElementsByTagName("form");
  for (let i = 0; i < forms.length; i++) {
    const ratingSunsForForm = [...forms[i].getElementsByClassName("bi bi-sun")];
    executeRating(ratingSunsForForm, forms[i]);
  }
});
document.addEventListener("DOMContentLoaded", function () {
  const accordionTitle = document.querySelectorAll(".helpTitle");
  const searchBox = document.getElementById("search");
  const searchForm = document.getElementById("searchForm");

  if (searchBox) {
    searchBox.addEventListener("input", (e) => {
      searchBox.value = e.target.value;

      searchTitle(searchBox.value);
    });

    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
    });
  }
  const searchTitle = (search) => {
    search = searchBox.value.toLowerCase();

    Array.from(accordionTitle, (title) => {
      const titleText = title.textContent.toLowerCase();
      const titleContainer = title.parentElement;

      if (titleText.includes(search)) {
        titleContainer.style.display = "block";
      } else {
        titleContainer.style.display = "none";
      }
    });
  };
});

document.addEventListener("DOMContentLoaded", function () {
  const searchInput = document.getElementById("search1");
  const postTitles = document.querySelectorAll(".postArticle");
  const searchForm1 = document.getElementById("searchForm1");

  if (searchInput) {
    searchForm1.addEventListener("submit", (e) => {
      e.preventDefault();
    });
    searchInput.addEventListener("input", (e) => {
      searchInput.value = e.target.value;
      searchPost(searchInput.value);
    });
  }

  const searchPost = (search) => {
    search = searchInput.value.toLowerCase();

    Array.from(postTitles, (title) => {
      const postText = title.textContent.toLowerCase();

      if (postText.includes(search)) {
        postText.style.display = "block";
      } else {
        postText.style.display = "none";
      }
    });
  };
});
