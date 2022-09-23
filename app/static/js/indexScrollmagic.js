const controller = new ScrollMagic.Controller();

const scene = new ScrollMagic.Scene({
    triggerElement:"#features",
})
.on('enter leave', function() {
    $('.card').toggleClass('showUp');
})
// .addIndicators()
.addTo(controller);