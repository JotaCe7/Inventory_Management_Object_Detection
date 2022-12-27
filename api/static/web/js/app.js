const image_input = document.querySelector("#image_input2");
var uploaded_image = ""

image_input.addEventListener("change", function() {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    uploaded_image = reader.result;
    var img_container = document.querySelector("#display_image2")
    img_container.style.backgroundImage = `url(${uploaded_image})`;
    image = new Image()
    image.src = uploaded_image
    img_container.style.width =  image.width + 'px'
    img_container.style.height = image.height + 'px'
  })
  reader.readAsDataURL(this.files[0]);
  // TODO: delete console.log
  console.log(this.files[0].name) 
})