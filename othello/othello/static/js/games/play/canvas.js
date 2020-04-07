class RCanvas {
  constructor(canvasDOM, rWidth, rHeight) {
    this.canvas = canvasDOM;
    this.ctx = this.canvas.getContext('2d');
    this.rWidth = rWidth;
    this.rHeight = rHeight;
    this.mx = this.my = 0;
    this.lBSize = 1;
    this.wFactor = this.canvas.width / this.rWidth;
    this.hFactor = this.canvas.height / this.rHeight;
    this.objects = [];
  }
  draw() {
    for(let obj in this.objects){
      if (this.objects.hasOwnProperty(obj)){
          this.objects[obj].draw(this.ctx, this.wFactor, this.hFactor);
      }
    }
  }
  resize() {
    let nWidth = this.canvas.offsetWidth * window.devicePixelRatio;
    let nHeight = this.canvas.offsetHeight * window.devicePixelRatio;
    console.log("SETTING",Math.min(nWidth, nHeight * this.rWidth / this.rHeight), Math.min(nHeight, nWidth * this.rHeight / this.rWidth));
    this.canvas.width = Math.min(nWidth, nHeight * this.rWidth / this.rHeight);
    this.canvas.height = Math.min(nHeight, nWidth * this.rHeight / this.rWidth);
    this.wFactor = this.canvas.width / this.rWidth;
    this.hFactor = this.canvas.height / this.rHeight;
    this.draw();
  }
  add(obj) {
    this.objects[this.objects.length] = obj;
  }
  getMousePos(event){
    let rect = this.canvas.getBoundingClientRect();
    this.mx = (event.clientX - rect.left) * this.rWidth / rect.width;
    this.my = (event.clientY - rect.top) * this.rHeight / rect.height;
  }
}


class RRect{
  constructor(x,y,width,height,fill,alpha) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.fill = fill;
    this.alpha = alpha;
  }
  draw(ctx, wFactor, hFactor){
    ctx.fillStyle = this.fill;
    ctx.globalAlpha = this.alpha;
    ctx.fillRect(this.x*wFactor, this.y*hFactor, this.width*wFactor, this.height*hFactor);
    ctx.globalAlpha = 1.0;
  }
}

class RText{
  constructor(x,y,text,size,font,fill) {
    this.x = x;
    this.y = y;
    this.text = text;
    this.size = size;
    this.font = font;
    this.fill = fill;
  }
  draw(ctx,wFactor,hFactor){
    ctx.fillStyle = this.fill;
    ctx.font = Math.floor((hFactor+wFactor)/2*size).toString()+'px '+this.font;
    ctx.fillText(this.text,this.x*wFactor,this.y*hFactor);
  }
}

class RImg{
  constructor(x,y,width,height,image,shadow) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.height = height;
    this.shadow = shadow || false;
    this.image = image;
  }
  draw(ctx, wFactor, hFactor){
    ctx.save();
    if (this.shadow) {
      ctx.shadowColor = "rgba(0,0,0,0.2)";
      ctx.shadowBlur = 5*wFactor;
      ctx.shadowOffsetX = 2*wFactor;
      ctx.shadowOffsetY = 2*hFactor;
    }
    if (this.image !== undefined && typeof(this.image) === "object") {
      ctx.drawImage(this.image, this.x*wFactor, this.y*hFactor, this.width*wFactor, this.height*hFactor);
    }
    ctx.restore();
    }
}

