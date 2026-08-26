/* MC.CN 新闻动态加载：从 assets/data/news.json 读取并自动滚动加载 */
(function () {
    var PAGE_SIZE = 10;
    var lists = document.querySelectorAll('.js-news-list');
    if (!lists.length) return;

    function renderItems(list, items, start, end) {
        var fragment = document.createDocumentFragment();
        for (var i = start; i < end && i < items.length; i++) {
            var item = items[i];
            var li = document.createElement('li');
            var a = document.createElement('a');
            a.href = item.url;
            a.target = '_blank';
            a.rel = 'noopener';
            a.textContent = item.title;
            li.appendChild(a);
            var span = document.createElement('span');
            span.className = 'date';
            span.textContent = item.date;
            if (item.source) {
                span.textContent = item.date + ' · ' + item.source;
            }
            li.appendChild(span);
            fragment.appendChild(li);
        }
        list.appendChild(fragment);
    }

    function initList(list) {
        var sentinel = list.parentNode.querySelector('.js-news-sentinel');
        var current = 0;
        var items = [];
        var observer = null;

        function showMore() {
            var next = current + PAGE_SIZE;
            renderItems(list, items, current, next);
            current = next;
            if (sentinel && current >= items.length && observer) {
                observer.disconnect();
            }
        }

        if (sentinel && 'IntersectionObserver' in window) {
            observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        showMore();
                    }
                });
            }, { rootMargin: '120px' });
            observer.observe(sentinel);
        }

        fetch('./assets/data/news.json', { cache: 'no-store' })
            .then(function (resp) {
                if (!resp.ok) throw new Error('HTTP ' + resp.status);
                return resp.json();
            })
            .then(function (data) {
                items = Array.isArray(data) ? data : [];
                showMore();
            })
            .catch(function () {
                items = window.MC_FALLBACK_NEWS || [];
                showMore();
            });
    }

    lists.forEach(initList);
})();
