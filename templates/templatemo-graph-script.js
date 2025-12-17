// templatemo-graph-script.js - Basic functionality for the dashboard

document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation toggle
    const hamburger = document.getElementById('hamburger');
    const navLinksMobile = document.getElementById('navLinksMobile');
    
    if (hamburger) {
        hamburger.addEventListener('click', function() {
            navLinksMobile.classList.toggle('active');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
                
                // Close mobile menu if open
                if (navLinksMobile.classList.contains('active')) {
                    navLinksMobile.classList.remove('active');
                }
            }
        });
    });
    
    // Form submission feedback
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            alert('Thank you for your message! We will get back to you soon.');
            this.reset();
        });
    }
    
    // Mini charts simulation (visual only)
    const miniCharts = document.querySelectorAll('.mini-chart');
    miniCharts.forEach(chart => {
        if (chart.getContext) {
            const ctx = chart.getContext('2d');
            ctx.canvas.width = 100;
            ctx.canvas.height = 30;
            
            // Draw a simple line chart
            ctx.beginPath();
            ctx.moveTo(0, 15);
            ctx.bezierCurveTo(20, 5, 40, 25, 60, 10);
            ctx.bezierCurveTo(80, 20, 90, 5, 100, 15);
            ctx.strokeStyle = '#00ffcc';
            ctx.lineWidth = 2;
            ctx.stroke();
        }
    });
});