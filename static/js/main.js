// This is the main script file which contains all
// the common functions of the template


// Pages
// *** OPEN PAGE ***
const pageOpenButtons = document.querySelectorAll('.open-page');
pageOpenButtons.forEach((btn) => {
    btn.onclick = (e) => {
        const triggeredPage = btn.dataset.page;
        document.querySelector(`.${triggeredPage}`).classList.toggle('active');
    }
});
// *** CLOSE PAGE ***
const closePages = document.querySelectorAll('.close-page');
closePages.forEach((item) => {
    item.onclick = (e) => {
        let triggerPage = item.dataset.closePage;
        document.querySelector(`.${triggerPage}`).classList.toggle('active');
    }
})


// Handle Search
const searchInput = document.getElementById('search-input');

searchInput.onkeyup = () => {
    let value = searchInput.value;
    if (value.length > 3) {
        search(value);
    }
}

function search(value) {
    clearItems();
    setLoader();
    let xhr = new XMLHttpRequest();
    xhr.open('GET', `/api/search?s=${value}`);
    xhr.onload = () => {
        let jsoned = JSON.parse(xhr.responseText);
        setItems(jsoned.datas);
    }
    xhr.onerror = () => {
        document.querySelector('.found-list').innerHTML = `<li class='result'><span class='en'>${xhr.responseText}</span></li>`;
    }
    xhr.send();
}

function setLoader() {
    document.querySelector('.found-list').innerHTML = '<li><span class="spinner"></span></li>';
}

function setItems(items) {
    clearItems();
    let all_els = '';
    items.forEach((item) => {
        let name = item.en_story ? item.title : item.name;
        let genres = "";
        if (item.genre) {
            item.genre.forEach((foo) => {
                genres += `<a href="/category/${foo}" class="genre-item en">${foo}</a>`;
            });
        }
        let image = item.en_story ? item.item_img : item.img;

        let rating = '';
        let url = item.url;
        if (item.rating) {
            rating = `<div class="rating">
            <i class="fas fa-star"></i>
            <p><span>${item.rating}</span> / 10</p>
        </div>`;
        }
        let item_el = `<li>
                <div class="left">
                    <div class="image" style="background-image: url(${image})"></div>
                    <div class="details">
                        <a class="title en" href="${url}">${name}</a>
                        <div class="genre">
                         ${genres}
                        </div> 
                    </div>
                </div>
                <div class="right">
                    ${rating}
                </div>
            </li>`;
        all_els += item_el;
    });
    document.querySelector('.found-list').innerHTML = all_els;
    if (items.length === 0) {
        document.querySelector('.found-list').innerHTML = "<li class='result'><span>نتیجه ای یافت نشد!</span></li>";
    }

}


function clearItems() {
    document.querySelector('.found-list').innerHTML = '';
}


const disabledLinks = document.querySelectorAll('.disabled');
disabledLinks.forEach(item => {
    item.onclick = (e) => {
        e.preventDefault();
    }
});

// Check Boxes
let checkLabels = document.querySelectorAll(".checkLabel");
checkLabels.forEach((item) => {
    let checkID = item.getAttribute("data-check-id");
    let checkEL = document.getElementById(checkID);
    if (checkEL.checked) {
        item.classList.add('active');
    }
    item.onclick = (e) => {
        checkEL.click();
        item.classList.toggle("active");
    };
});


//let links = `https://eu.cdn.cloudam.cc/download/2/1/911896/1361368/587766/98.98.166.58/1693005057/3094147195ad54fdfa1aedeab96297145ad3eccf55/series/Silo/Silo_S01E01_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361369/587766/98.98.166.58/1693005057/3037bde891947570cf9c23dec074248d833e929d5c/series/Silo/Silo_S01E02_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361370/587766/98.98.166.58/1693005057/30f7714870f5fd6e29d35c9eaea4ab6e67a4056edf/series/Silo/Silo_S01E03_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361371/587766/98.98.166.58/1693005057/304dbfcd5d0da7aca62b447d156abcb903f44b0e8d/series/Silo/Silo_S01E04_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361372/587766/98.98.166.58/1693005057/3070d846d9778f972400f3420f56ba926f74c26ad2/series/Silo/Silo_S01E05_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361373/587766/98.98.166.58/1693005057/30c51c826833e656c467c008747cf9421b16329fcc/series/Silo/Silo_S01E06_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361374/587766/98.98.166.58/1693005057/30b1916b82ac7c95c6a99cb8d85ba0152cd3dd4ccb/series/Silo/Silo_S01E07_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361375/587766/98.98.166.58/1693005057/30b53e6c19976b5ad9f93110532218a93d81569ea3/series/Silo/Silo_S01E08_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361377/587766/98.98.166.58/1693005057/30b898196d14b515291bc33b2a805a08b682f288bd/series/Silo/Silo_S01E09_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv
//https://eu.cdn.cloudam.cc/download/2/1/911896/1361386/587766/98.98.166.58/1693005057/30b8f30d81e32eae84b157588acfeae47050feb07a/series/Silo/Silo_S01E10_10bit_x265_1080p_WEB-DL_t3nzin_30NAMA.mkv`;

//let links_list = links.split('.mkv');

//links_list.forEach((link) => {
  //  let url = link.replace('\n', '');
    //url = url + '.mkv';
    //console.log(url);
    //if (url !== "") {
      //  window.open(url, '_blank');
    //}
//});
