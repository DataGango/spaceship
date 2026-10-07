(() => {
  const canvas = document.querySelector('#concept-board');
  const context = canvas.getContext('2d');
  const button = document.querySelector('#start');
  const status = document.querySelector('#concept-status');
  const medical = document.body.dataset.concept === 'medical';
  let elapsed = 0, running = false, previous = null, frame = 0;
  const duration = 10000;
  function draw() {
    const progress = elapsed / duration;
    context.clearRect(0, 0, 960, 480);
    context.fillStyle = '#f8fbfb';context.fillRect(0, 0, 960, 480);
    if (medical) {
      const extension = Math.sin(progress * Math.PI);
      context.fillStyle = '#e3efeb';context.fillRect(310, 100, 340, 270);
      for (const side of [-1, 1]) {
        const base = [480 + side * 310, 340], joint = [480 + side * (230 - extension * 50), 145];
        const tip = [480 + side * (170 - extension * 115), 240 + side * 30 * extension];
        context.strokeStyle = '#d8a534';context.lineWidth = 2;context.beginPath();context.arc(480 + side * 55,240 + side * 30,18,0,Math.PI*2);context.stroke();
        context.strokeStyle = '#385862';context.lineWidth = 20;context.lineCap = 'round';context.beginPath();context.moveTo(...base);context.lineTo(...joint);context.lineTo(...tip);context.stroke();
        for (const point of [base, joint, tip]) {context.fillStyle='#176c62';context.beginPath();context.arc(...point,point===tip?7:16,0,Math.PI*2);context.fill();}
      }
    } else {
      context.strokeStyle='#d0e1e4';context.lineWidth=60;context.beginPath();context.moveTo(80,240);context.bezierCurveTo(290,80,530,380,790,240);context.stroke();
      context.strokeStyle='#d8a534';context.lineWidth=3;context.beginPath();context.arc(790,240,42,0,Math.PI*2);context.stroke();
      const travel=Math.min(1,progress/.65),positionX=100+690*travel,positionY=240-50*Math.sin(travel*Math.PI*2);
      context.fillStyle='#176c62';context.fillRect(positionX-20,positionY-12,40,24);context.fillStyle='#d2e6e1';context.fillRect(positionX-12,positionY-7,12,14);
      if(progress>.65){const spread=(progress-.65)/.35;for(let index=0;index<8;index++){const angle=index*Math.PI/4;context.fillStyle='#bd6954';context.beginPath();context.arc(790+Math.cos(angle)*spread*30,240+Math.sin(angle)*spread*30,4,0,Math.PI*2);context.fill();}}
    }
    context.fillStyle='#637478';context.font='16px sans-serif';context.fillText('EDUCATIONAL CONCEPT ONLY / NOT A CLINICAL PROCEDURE',30,450);
  }
  function animate(timestamp) {
    if(!running)return;
    if(previous!==null)elapsed=Math.min(duration,elapsed+Math.min(timestamp-previous,100)*Number(document.querySelector('#speed').value));
    previous=timestamp;draw();
    status.textContent=medical?(elapsed<duration/2?'Abstract pointer alignment':'Returning to rest'):(elapsed<6500?'Symbolic carrier navigation':'Illustrative payload display');
    if(elapsed>=duration){running=false;previous=null;button.textContent='Replay demonstration';status.textContent='Demonstration complete';return;}
    frame=requestAnimationFrame(animate);
  }
  button.onclick=()=>{if(running){running=false;cancelAnimationFrame(frame);previous=null;button.textContent='Resume demonstration';status.textContent='Paused';return;}if(elapsed>=duration)elapsed=0;running=true;button.textContent='Pause demonstration';status.textContent='Demonstration running';frame=requestAnimationFrame(animate);};
  document.querySelector('#reset').onclick=()=>{running=false;cancelAnimationFrame(frame);elapsed=0;previous=null;button.textContent='Start demonstration';status.textContent='Ready';draw();};
  document.addEventListener('visibilitychange',()=>{previous=null;});
  draw();
})();