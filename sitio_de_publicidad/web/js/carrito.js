var Carrito = {
  getItems: function () {
    return JSON.parse(localStorage.getItem("apomat_carrito") || "[]");
  },
  setItems: function (items) {
    localStorage.setItem("apomat_carrito", JSON.stringify(items));
    this.actualizarBadge();
    this.renderizarOffcanvas();
  },
  agregar: function (producto, cantidad) {
    if (cantidad === undefined) cantidad = 1;
    var items = this.getItems();
    var idx = items.findIndex(function (i) { return i.id === producto.id; });
    if (idx >= 0) {
      items[idx].cantidad += cantidad;
    } else {
      items.push({
        id: producto.id,
        nombre: producto.nombre,
        precio: producto.precio_rebaja || producto.precio,
        imagen: producto.imagen,
        cantidad: cantidad
      });
    }
    this.setItems(items);
  },
  eliminar: function (id) {
    this.setItems(this.getItems().filter(function (i) { return i.id !== id; }));
  },
  actualizarCantidad: function (id, cantidad) {
    var items = this.getItems();
    var item = items.find(function (i) { return i.id === id; });
    if (item) {
      item.cantidad = cantidad;
      if (item.cantidad <= 0) {
        this.eliminar(id);
      } else {
        this.setItems(items);
      }
    }
  },
  vaciar: function () {
    this.setItems([]);
    localStorage.removeItem("apomat_carrito_backup" + (this._userId ? "_" + this._userId : ""));
  },
  getTotal: function () {
    var items = this.getItems();
    var total = 0;
    for (var i = 0; i < items.length; i++) {
      total += items[i].precio * items[i].cantidad;
    }
    return total;
  },
  getCantidadTotal: function () {
    var items = this.getItems();
    var count = 0;
    for (var i = 0; i < items.length; i++) {
      count += items[i].cantidad;
    }
    return count;
  },
  formatearPrecio: function (precio) {
    return "$ " + precio.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ".");
  },
  actualizarBadge: function () {
    var count = this.getCantidadTotal();
    document.querySelectorAll(".cart-badge").forEach(function (b) {
      b.textContent = count;
      b.style.display = count > 0 ? "inline" : "none";
    });
  },
  renderizarOffcanvas: function () {
    var container = document.getElementById("cart-offcanvas-body");
    if (!container) return;
    var items = this.getItems();
    if (items.length === 0) {
      container.innerHTML =
        '<div class="text-center py-5 text-muted"><i class="bi bi-cart-x" style="font-size:3rem;display:block;margin-bottom:1rem;"></i>Tu carrito está vacío</div>';
      return;
    }
    var html = '<ul class="cart-items-list">';
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      html +=
        '<li class="cart-item" data-id="' + item.id + '">' +
        '<img src="/site/img/' + item.imagen + '" alt="' + item.nombre + '" class="cart-item-img">' +
        '<div class="cart-item-info">' +
        '<span class="cart-item-name">' + item.nombre + '</span>' +
        '<span class="cart-item-price">' + this.formatearPrecio(item.precio) + '</span>' +
        '<div class="cart-qty-controls">' +
        '<button class="cart-qty-btn" onclick="Carrito.actualizarCantidad(' + item.id + ', ' + (item.cantidad - 1) + ')">-</button>' +
        '<span class="cart-qty">' + item.cantidad + '</span>' +
        '<button class="cart-qty-btn" onclick="Carrito.actualizarCantidad(' + item.id + ', ' + (item.cantidad + 1) + ')">+</button>' +
        '</div></div>' +
        '<button class="cart-item-remove" onclick="Carrito.eliminar(' + item.id + ')" title="Eliminar"><i class="bi bi-trash"></i></button>' +
        '</li>';
    }
    html += '</ul>';
    html +=
      '<div class="cart-footer">' +
      '<div class="cart-total"><span>Total</span><span>' + this.formatearPrecio(this.getTotal()) + '</span></div>' +
      '<a href="/checkout" class="btn btn-gold w-100">Ir a pagar</a>' +
      '</div>';
    container.innerHTML = html;
  }
};

function mostrarToastCarrito(nombre) {
  if (typeof Swal !== "undefined") {
    Swal.fire({
      text: nombre + " — Agregado al carrito",
      toast: true,
      position: "top",
      timer: 1800,
      showConfirmButton: false,
      width: "auto",
      padding: "0.5rem 1rem",
      customClass: {
        popup: "swal-brand-popup toast-carrito",
        htmlContainer: "swal-brand-text"
      }
    });
  }
}

document.addEventListener("DOMContentLoaded", function () {
  fetch('/usuario?t=' + Date.now(), { cache: 'no-store' })
    .then(function (r) { return r.json(); })
    .then(function (d) {
      if (d && !d.error) {
        var userId = d.id || 0;
        var storedId = localStorage.getItem("apomat_carrito_user");
        if (storedId !== null && storedId !== String(userId)) {
          localStorage.removeItem("apomat_carrito");
        }
        localStorage.setItem("apomat_carrito_user", String(userId));
      } else {
        var storedId = localStorage.getItem("apomat_carrito_user");
        if (storedId !== null && storedId !== "0") {
          localStorage.removeItem("apomat_carrito");
          localStorage.setItem("apomat_carrito_user", "0");
        }
      }
      Carrito.actualizarBadge();
      Carrito.renderizarOffcanvas();
    })
    .catch(function () {
      Carrito.actualizarBadge();
      Carrito.renderizarOffcanvas();
    });
});
