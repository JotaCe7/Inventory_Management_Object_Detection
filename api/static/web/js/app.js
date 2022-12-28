const image_input = document.querySelector("#uploaded_img");
var uploaded_image = ""

image_input.addEventListener("change", function() {
  const reader = new FileReader();
  reader.addEventListener("load", () => {
    uploaded_image = reader.result;
    var imgtag = document.getElementById("my_preview");
    imgtag.src = uploaded_image;

  })
  reader.readAsDataURL(this.files[0]);
  // TODO: delete console.log
  console.log(this.files[0].name) 
  
})