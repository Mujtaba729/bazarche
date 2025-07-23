document.addEventListener('DOMContentLoaded', function() {
  // Infinite scroll for product list
  const productListContainer = document.querySelector('.col-lg-9 > .row');
  if (!productListContainer) return;

  let currentPage = 1;
  let loading = false;
  let hasNext = true;

  window.addEventListener('scroll', () => {
    if (loading || !hasNext) return;

    if ((window.innerHeight + window.scrollY) >= (document.body.offsetHeight - 300)) {
      loading = true;
      currentPage += 1;

      const params = new URLSearchParams(window.location.search);
      params.set('page', currentPage);

      fetch(window.location.pathname + '?' + params.toString(), {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.html) {
          const tempDiv = document.createElement('div');
          tempDiv.innerHTML = data.html;
          while (tempDiv.firstChild) {
            productListContainer.appendChild(tempDiv.firstChild);
          }
          hasNext = data.has_next;
          loading = false;
        }
      })
      .catch(() => {
        loading = false;
      });
    }
  });
});
