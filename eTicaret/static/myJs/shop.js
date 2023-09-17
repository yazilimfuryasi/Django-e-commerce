// Ürün Sıralama
// $(document).ready(function () {
//     $('#sirala').on('change', function () {
//         var secilenSecenek = $(this).val();
//         var currentPath = $('#my-element').data('current-path');
//         var url = currentPath + '?sirala=' + encodeURIComponent(secilenSecenek);
//         window.location.href = url;
//     });
// });

$(document).ready(function () {
  // Ürün Sıralama
  $('#sirala').on('change', function () {
    var secilenSecenek = $(this).val();
    var currentPath = $('#my-element').data('current-path');
    var max_price = urlParams.get('max_price');
    var min_price = urlParams.get('min_price');
    var url = currentPath + "?sirala=" + secilenSecenek;
    if (max_price && min_price)
      url += "&min_price=" + min_price + "&max_price=" + max_price;
    window.location.href = url;
  });

  // Fiyat Filtresi
  var minPriceValue = 10;
  var maxPriceValue = 1000;

  function updateSliderValues(minValue, maxValue) {
    $("#display-min-price").text(minValue);
    $("#display-max-price").text(maxValue);
  }

  var urlParams = new URLSearchParams(window.location.search);
  var minPriceParam = urlParams.get('min_price');
  var maxPriceParam = urlParams.get('max_price');

  if (minPriceParam !== null && maxPriceParam !== null) {
    // minPriceValue = parseInt(minPriceParam);
    // maxPriceValue = parseInt(maxPriceParam);
    var parsedMinPrice = parseInt(minPriceParam);
    var parsedMaxPrice = parseInt(maxPriceParam);
    console.log(parsedMaxPrice)
    if (!isNaN(parsedMinPrice) && !isNaN(parsedMaxPrice) && parsedMinPrice >= 0 && parsedMaxPrice <= 1000 && parsedMinPrice < parsedMaxPrice) {
      minPriceValue = parsedMinPrice;
      maxPriceValue = parsedMaxPrice;
    }
    else {
      var currentPath = $('#my-element').data('current-path');
      window.location.href = currentPath;
      return;
    }
  }

  $('.slider-range-price').each(function () {
    var min = $(this).data('min');
    var max = $(this).data('max');
    var unit = $(this).data('unit');
    var label_result = $(this).data('label-result');
    var t = $(this);

    t.slider({
      range: true,
      min: min,
      max: max,
      step: 10,
      values: [minPriceValue, maxPriceValue],
      slide: function (event, ui) {
        var result = label_result + " " + unit + ui.values[0] + ' - ' + unit + ui.values[1];
        t.closest('.slider-range').find('.range-price').html(result);
        updateSliderValues(ui.values[0], ui.values[1]);
      },
      stop: function (event, ui) {
        var minPrice = ui.values[0];
        var maxPrice = ui.values[1];
        var currentPath = $('#my-element').data('current-path');
        var url = "?min_price=" + encodeURIComponent(minPrice) + '&max_price=' + encodeURIComponent(maxPrice)
        sortOption = urlParams.get('sirala');
        
        if (sortOption) {url += "&sirala="+sortOption;}
        window.location.href = url;
      }
    });

    updateSliderValues(minPriceValue, maxPriceValue);
  });
});





// Sepete Ürün Ekle
$(document).ready(function() {
    $(".add-to-cart-button").click(function(event) {
      event.preventDefault();
  
      const productId = $(this).data("product-id");
      const csrfToken = $("input[name='csrfmiddlewaretoken']").val();
      const quantity = $("#qty").val();
        console.log("geldi: ", productId, quantity);
      $.ajax({
        type: "POST",
        url: "/add_to_cart/",
        data: {
          'product_id': productId,
          'quantity': quantity,
          'csrfmiddlewaretoken': csrfToken,
        },
        success: function(response) {
            $("#addToCartModal").modal('show');
          $("#cart-item-count").text('(' + response.cart_item_count + ')');
          console.log(response);
          setTimeout(function() {
            $("#addToCartModal").modal('hide');
          }, 2000); // 2000 milisaniye (2 saniye)
        },
        error: function(error) {
          alert("An error occurred.");
        }
      });
    });
});


$('.sepet-urun-sil').click(function() {
  var productId = $(this).data('product-id');
  const csrfToken = $("input[name='csrfmiddlewaretoken']").val();

  $.ajax({
      type: 'POST',
      url: '/sepet/remove/' + productId + '/',
      data: {
          product_id: productId,
          'csrfmiddlewaretoken': csrfToken,
      },
      success: function(data) {
        console.log(data.status);
          if (data.status === 'success') {
              // Eğer düzenleme başarılı ise, sayfayı yenileme yerine sepetteki sayfaya yönlendir
              location.reload();
          }
      },
      error: function(xhr, errmsg, err) {
          console.log('Error:', errmsg);
      }
  });
});
