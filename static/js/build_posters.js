function BuildPosters(posters) {
    posters.forEach((poster) => {
        let img_el = document.createElement('img');
        img_el.src = poster.poster_img;
        img_el.className = "animate__animated animate__fadeIn";
        document.querySelector('.images').append(img_el);
        let title_el = document.createElement('h2');
        title_el.innerText = poster.title;
        title_el.className = "en animate__animated animate__fadeIn";
        document.querySelector('.titles').append(title_el);
    });

    const images = document.querySelector('.images').querySelectorAll('img');
    const titles = document.querySelector('.titles').querySelectorAll('h2');
    const onlineBtn = document.getElementById('play-online-btn');
    let timer = setInterval(changeStat, 7000);
    let current = 0;
    function changeStat() {
        if (current === images.length - 1) {
            current = 0;
        } else {
            current += 1
        }
        hideAll();
        images[current].style.display = 'unset';
        titles[current].style.display = 'unset';
        onlineBtn.href = posters[current].slug;

    }

    function hideAll() {
        if (images.length > 0) {
            images.forEach((image) => {
                image.style.display = 'none';
            })
            titles.forEach((title) => {
                title.style.display = 'none';
            });
        }
    }

}

