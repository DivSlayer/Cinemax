class SingleCarousel {
    constructor(container_id, use_pagination = false, speed = 3000, spaceSize = 20) {
        this.container = document.getElementById(container_id);
        this.list = this.container.querySelector('.items-list');
        this.items = this.list.querySelectorAll('li');
        this.spaceSize = spaceSize;
        this.mainSize = this.container.clientWidth;
        this.speed = speed;
        this.timer = undefined;
        this.pagination = undefined;
        this.use_pagination = use_pagination;
        this.activeItem = 0;
        if (use_pagination) {
            this.setPagination();
            this.paginationEvents();
        }
        this.changeStatus();
        this.setTimer();
        this.handleEvents();
    }

    changeStatus() {
        if (this.use_pagination) {
            let pages = this.pagination.querySelector('.items-list').querySelectorAll('li');
            pages.forEach((page) => {
                page.classList.remove('active');
            })
            pages[this.activeItem].classList.add('active');
        }
        this.items.forEach((item) => {
            item.style.width = `${this.mainSize}px`;
        });
        this.setTransform();
    }

    setTransform() {
        let totalTranform = this.activeItem * this.mainSize;
        this.list.style.transform = `translateX(${totalTranform}px)`;
    }

    setTimer() {
        this.timer = setInterval(() => {
            if (this.activeItem < this.items.length - 1) {
                this.activeItem += 1;
            } else {
                this.activeItem = 0;
            }
            this.changeStatus();
        }, this.speed);
    }

    handleEvents() {
        let isDragging = false;
        let firstTouch = 0;
        this.container.ontouchstart = (e) => {
            clearInterval(this.timer);
            touchStart(e);
        };
        this.container.ontouchend = (e) => {
            touchEnd(e);
            this.setTimer();
        };
        this.container.ontouchmove = (e) => {
            let actItem = touchMove(e, this.items, this.list, this.activeItem, this.normalWidth, this.spaceSize);
            if (actItem !== this.activeItem) {
                this.activeItem = actItem;
                this.changeStatus();
            }
        };

        this.container.onmousedown = (e) => {
            touchStart(e)
        };
        this.container.onmouseup = (e) => {
            touchEnd()
        };
        this.container.onmousemove = (e) => {
            let actItem = touchMove(e, this.items, this.list, this.activeItem, this.normalWidth, this.spaceSize);
            if (actItem !== this.activeItem) {
                this.activeItem = actItem;
                this.changeStatus();
            }
        };

        this.container.onmouseenter = () => {
            clearInterval(this.timer);
        }
        this.container.onmouseleave = () => {
            this.setTimer();
        }

        function touchStart(e) {
            e.preventDefault();
            isDragging = true;
            firstTouch = e.screenX;
        }

        function touchEnd() {
            isDragging = false;
        }

        function touchMove(e, items, list, activeItem, normalWidth, spaceSize) {
            e.preventDefault();
            let differ = e.screenX - firstTouch;
            if (isDragging) {
                let totalTranform = (activeItem * normalWidth) - normalWidth + 4 * spaceSize + differ;
                list.style.transform = `translateX(${totalTranform}px)`;
                if (differ > 100) {
                    if (activeItem < items.length - 1) {
                        activeItem += 1;
                    }
                    isDragging = false;
                }
                if (differ < -100) {
                    if (activeItem > 0) {
                        activeItem -= 1;
                    }
                    isDragging = false;
                }
            }
            return activeItem;
        }
    }

    setPagination() {
        let parentEl = this.container.parentElement;
        let paginationEl = document.createElement('div');
        paginationEl.className = 'carousel-pagination';
        let listEl = document.createElement('ul');
        listEl.className = 'items-list';
        let itemsEl = '';
        this.items.forEach(element => {
            itemsEl += '<li></li>';
        });
        listEl.innerHTML = itemsEl;
        paginationEl.appendChild(listEl);
        let container_index = Array.from(parentEl.children).indexOf(this.container);
        parentEl.insertBefore(paginationEl, parentEl.children[container_index + 1]);
        this.pagination = document.querySelector('.carousel-pagination');
    }

    paginationEvents() {
        let pages = this.pagination.querySelector('.items-list').querySelectorAll('li');
        pages.forEach((page) => {
            page.addEventListener('click', () => {
                let index = Array.from(pages).indexOf(page);
                clearInterval(this.timer);
                this.activeItem = index;
                this.changeStatus();
                this.setTimer();
            });
        })
    }
}

export default SingleCarousel;