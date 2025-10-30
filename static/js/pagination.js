function MakePagination(current, last, first) {
    let all_together = '';
    let dot_el = '<li class="dot"></li>';
    if (last >= 10) {
        if (current < 5 || current > (last - 4)) {
            // First Five
            let first_five = '';
            for (let i = first; i <= 5; i++) {
                let url = window.location.search === "" ? `?page=${i}` : `${window.location.search}&page=${i}`;
                let li_el = `<li class="${i === current ? 'active' : ''}"><a href="${url}" class="${i === current ? 'disabled' : ''}"><span>${i}</span></a></li>`;
                first_five += li_el;
            }
            // Second Five
            let second_five = '';
            for (let i = last - 4; i <= last; i++) {
                let url = window.location.search === "" ? `?page=${i}` : `${window.location.search}&page=${i}`;
                let li_el = `<li class="${i === current ? 'active' : ''}"><a href="${url}" class="${i === current ? 'disabled' : ''}"><span>${i}</span></a></li>`;
                second_five += li_el;
            }
            all_together += first_five + dot_el + dot_el + dot_el + second_five;
        } else {
            let left_group = '';
            for (let i = 1; i < 4; i++) {
                let url = window.location.search === "" ? `?page=${i}` : `${window.location.search}&page=${i}`;
                let li_el = `<li class="${i === current ? 'active' : ''}"><a href="${url}" class="${i === current ? 'disabled' : ''}"><span>${i}</span></a></li>`;
                left_group += li_el;
            }
            let middle_group = '';
            for (let i = current - 2; i <= current + 2; i++) {
                let url = window.location.search === "" ? `?page=${i}` : `${window.location.search}&page=${i}`;
                let li_el = `<li class="${i === current ? 'active' : ''}"><a href="${url}" class="${i === current ? 'disabled' : ''}"><span>${i}</span></a></li>`;
                middle_group += li_el;
            }
            let right_group = '';
            for (let i = last - 2; i <= last; i++) {
                let url = window.location.search === "" ? `?page=${i}` : `${window.location.search}&page=${i}`;
                let li_el = `<li class="${i === current ? 'active' : ''}"><a href="${url}" class="${i === current ? 'disabled' : ''}"><span>${i}</span></a></li>`;
                right_group += li_el;
            }
            all_together = left_group + dot_el + middle_group + dot_el + right_group
        }
    } else {
        let all = '';
        for (let i = 1; i < last+1; i++) {
            let url = window.location.search === "" ? `?page=${i}` : `${window.location.search}&page=${i}`;
            let li_el = `<li class="${i === current ? 'active' : ''}"><a href="${url}" class="${i === current ? 'disabled' : ''}"><span>${i}</span></a></li>`;
            all += li_el;
        }
        all_together = all;
    }
    return all_together;
}


function Paginator(current, last, first) {
    document.querySelector('.pagination').querySelector('.links').innerHTML = MakePagination(current, last, first);
}


function setLocationAttr(attr) {

}
