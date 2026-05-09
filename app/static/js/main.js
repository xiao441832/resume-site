$(function () {
  var $backToTop = $(".back-to-top");

  $(window).on("scroll", function () {
    $backToTop.toggle($(this).scrollTop() > 320);
  });

  $backToTop.on("click", function () {
    $("html, body").animate({ scrollTop: 0 }, 240);
  });

  $(".navbar-collapse .nav-link").on("click", function () {
    var nav = bootstrap.Collapse.getInstance(document.getElementById("mainNav"));
    if (nav) {
      nav.hide();
    }
  });

  $("[data-confirm]").on("click", function (event) {
    if (!window.confirm($(this).data("confirm"))) {
      event.preventDefault();
    }
  });

  $("[data-preview-target]").on("change", function () {
    var input = this;
    var target = $(input).data("preview-target");
    var file = input.files && input.files[0];
    if (!target || !file) {
      return;
    }

    var reader = new FileReader();
    reader.onload = function (event) {
      $(target).attr("src", event.target.result).removeClass("d-none");
    };
    reader.readAsDataURL(file);
  });
});
