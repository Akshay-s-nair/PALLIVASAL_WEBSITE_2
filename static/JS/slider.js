document.addEventListener('DOMContentLoaded', function () {
    var sliders = document.querySelectorAll('.slider');
  
    sliders.forEach(function (slider) {
      var images = slider.querySelectorAll('img');
      var currentImageIndex = 0;
  
      for (var i = 1; i < images.length; i++) {
        images[i].style.display = 'none';
      }
  
      setInterval(function () {
        images[currentImageIndex].style.display = 'none';
        currentImageIndex++;
  
        if (currentImageIndex >= images.length) {
          currentImageIndex = 0;
        }
  
        images[currentImageIndex].style.display = 'block';
      }, 2000);
    });
  });
  