function RCanvas(canvasObj, rWidth, rHeight){
  this.canvas = canvasObj;
  this.ctx = this.canvas.getContext('2d');
  this.rWidth = rWidth;
  this.rHeight = rHeight;
  this.wFactor = this.canvas.width / this.rWidth;
  this.hFactor = this.canvas.height / this.rHeight;
  this.objects = [];
  this.draw = function(){
    for(var obj in this.objects){
      if (this.objects.hasOwnProperty(obj)){
        this.objects[obj].draw(this.ctx, this.wFactor, this.hFactor);
      }
    }
  };
  this.resize = function(){
    var nWidth = this.canvas.offsetWidth * window.devicePixelRatio;
    var nHeight = this.canvas.offsetHeight * window.devicePixelRatio;
    this.canvas.width = Math.min(nWidth, nHeight * this.rWidth / this.rHeight);
    this.canvas.height = Math.min(nHeight, nWidth * this.rHeight / this.rWidth);
    this.wFactor = this.canvas.width / this.rWidth;
    this.hFactor = this.canvas.height / this.rHeight;
    this.draw();
  };
  this.add = function(obj){
    this.objects[this.objects.length] = obj;
  };
  this.mx = 0;
  this.my = 0;
  this.getMousePos = function(event) {
    var rect = this.canvas.getBoundingClientRect();
    this.mx = (event.clientX - rect.left) * this.rWidth / rect.width;
    this.my = (event.clientY - rect.top) * this.rHeight / rect.height;
  };
  this.lBSize = 1;
}

function RRect(x,y,width,height,fill,alpha){
  this.x = x;
  this.y = y;
  this.width = width;
  this.height = height;
  this.fill = fill;
  this.alpha = alpha;
  this.draw = function(ctx, wFactor, hFactor){
    ctx.fillStyle = this.fill;
    ctx.globalAlpha = this.alpha;
    ctx.fillRect(this.x*wFactor, this.y*hFactor, this.width*wFactor, this.height*hFactor);
    ctx.globalAlpha = 1.0;
  };
}

function RText(x,y,text,size,font,fill){
  this.x = x;
  this.y = y;
  this.text = text;
  this.size = size;
  this.font = font;
  this.fill = fill;
  this.draw = function(ctx,wFactor,hFactor){
    ctx.fillStyle = this.fill;
    ctx.font = Math.floor((hFactor+wFactor)/2*size).toString()+'px '+this.font;
    ctx.fillText(this.text,this.x*wFactor,this.y*hFactor);
  };
}

function RImg(x,y,width,height,image,shadow){
  this.x = x;
  this.y = y;
  this.width = width;
  this.height = height;
  this.shadow = shadow || false;
  this.image = image;
  this.draw = function(ctx, wFactor, hFactor){
    ctx.save();
    if (this.shadow) {
      ctx.shadowColor = "rgba(0,0,0,0.2)";
      ctx.shadowBlur = 5*wFactor;
      ctx.shadowOffsetX = 2*wFactor;
      ctx.shadowOffsetY = 2*hFactor;
    }
    if (this.image !== undefined) {
      ctx.drawImage(this.image, this.x*wFactor, this.y*hFactor, this.width*wFactor, this.height*hFactor);
    }
    ctx.restore();
  };
}
