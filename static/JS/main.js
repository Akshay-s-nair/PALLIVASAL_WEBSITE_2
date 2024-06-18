var loader = document.getElementById("preloader");

window.addEventListener("load",function(){
  loader.style.display = "none";
})

function debounce(func, wait = 20, immediate = true) {
    var timeout;
    return function () {
        var context = this,
            args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

function checkSlide() {
    var headings = document.querySelectorAll("h1");

    headings.forEach(function (heading) {
        var contentPosition = heading.getBoundingClientRect().top;
        var viewHeight = window.innerHeight;

        if (contentPosition < viewHeight) {
            heading.classList.add("visible");
            heading.classList.remove("hidden");
        } else {
            heading.classList.add("hidden");
            heading.classList.remove("visible");
        }
    });
}

document.addEventListener("scroll", debounce(checkSlide));



let slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
showSlides(slideIndex += n);
}

function currentSlide(n) {
showSlides(slideIndex = n);
}

function showSlides(n) {
let i;
let slides = document.getElementsByClassName("mySlides");
let dots = document.getElementsByClassName("dot");
let sliderContainer = document.querySelector(".slideshow-container");

if (slides.length === 0) {
    console.error("No slides found.");
    sliderContainer.style.display = "none";
    return;
}

sliderContainer.style.display = "block"; 

if (n > slides.length) { slideIndex = 1 }
if (n < 1) { slideIndex = slides.length }
for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
}
for (i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
}
slides[slideIndex-1].style.display = "block";
if (dots.length > 0) {
    dots[slideIndex-1].className += " active";
}
}

function autoShowSlides() {
slideIndex++;
showSlides(slideIndex);
setTimeout(autoShowSlides, 10000); 
}

autoShowSlides();
