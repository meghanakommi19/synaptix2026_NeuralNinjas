const canvas = document.getElementById("bg");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];

for(let i=0;i<100;i++){
    particles.push({
        x: Math.random()*canvas.width,
        y: Math.random()*canvas.height,
        r: Math.random()*3,
        d: Math.random()*2
    });
}

function draw(){
    ctx.clearRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle="white";

    particles.forEach(p=>{
        ctx.beginPath();
        ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
        ctx.fill();

        p.y += p.d;
        if(p.y > canvas.height){
            p.y = 0;
        }
    });

    requestAnimationFrame(draw);
}

draw();
