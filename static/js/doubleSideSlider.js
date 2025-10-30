class DoubleSideSlider {
    constructor(upperSlider, lowerSlider, upperNumberEl, lowerNumberEl, setElText=false) {
        this.lowerSlider = document.getElementById(lowerSlider);
        this.upperSlider = document.getElementById(upperSlider);
        this.lowerNumberEl = document.getElementById(lowerNumberEl);
        this.upperNumberEl = document.getElementById(upperNumberEl);
        this.lowerNum = parseFloat(this.lowerSlider.value) / 10;
        this.upperNum = parseFloat(this.upperSlider.value) / 10;
        if (setElText){
            this.lowerNumberEl.innerText = `${this.lowerNum}`;
            this.upperNumberEl.innerText = `${this.upperNum}`;
        }

        this.lowerPoint = parseFloat(this.lowerSlider.value);
        this.upperPoint = parseFloat(this.upperSlider.value);
        this.differ = parseFloat(this.upperNum) - parseFloat(this.lowerNum);
        this.uppserEvent();
        this.lowerEvent();
    }

    lowerEvent() {
        this.lowerSlider.oninput = (e) => {
            let value = parseFloat(e.target.value);
            console.log(value);
            if (value >= this.upperPoint) {
                e.target.value = `${this.upperPoint}`;
            } else {
                this.lowerPoint = parseFloat(e.target.value);
                console.log(`differ: ${this.differ}, lowerP: ${this.lowerPoint},upperP: ${this.upperPoint}, lowerNum: ${this.lowerNum}, upperNum:${this.upperNum}`);
                this.lowerNumberEl.innerText =
                    Math.ceil(this.differ * (this.lowerPoint / 100)) + this.lowerNum;
            }
        };
    }

    uppserEvent() {
        this.upperSlider.oninput = (e) => {
            let value = parseFloat(e.target.value);
            if (value <= this.lowerPoint) {
                e.target.value = `${this.lowerPoint}`;
            } else {
                this.upperPoint = parseFloat(e.target.value);
                this.upperNumberEl.innerText =
                    this.upperNum -
                    Math.ceil(this.differ * ((100 - this.upperPoint) / 100));
            }
        };
    }
}

export default DoubleSideSlider;
  