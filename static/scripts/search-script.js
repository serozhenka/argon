const algoliaClient = algoliasearch('M89G8K0SXM', '5a2626dd2a640da591855e1711bf63ad');

const searchClient = {
  ...algoliaClient,
  search(requests) {
    if (requests.every(({ params }) => !params.query)) {
      return Promise.resolve({
        results: requests.map(() => ({
          hits: [],
          nbHits: 0,
          nbPages: 0,
          page: 0,
          processingTimeMS: 0,
        })),
      });
    }

    return algoliaClient.search(requests);
  },
};

const search = instantsearch({
  indexName: 'argon_Account',
  searchClient,
});


let lastRenderArgs;
let insertContainer

const infiniteHits = instantsearch.connectors.connectInfiniteHits(
  (renderArgs, isFirstRender) => {
    const { hits, showMore, widgetParams, results } = renderArgs;
    const { container } = widgetParams;

    if (lastRenderArgs?.results) {
      if (results.query !== lastRenderArgs.results?.query) {
        container.querySelector('ul').innerHTML = ""
      }
    }
    lastRenderArgs = renderArgs;

    if (isFirstRender) {
      const sentinel = document.createElement('div');
      container.appendChild(document.createElement('ul'));
      container.appendChild(sentinel);
      insertContainer = container.querySelector('ul');

      const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          if (entry.isIntersecting && !lastRenderArgs.isLastPage) {
            showMore();
          }
        });
      });

      observer.observe(sentinel);
      return null;
    }

    if (results.hits.length === 0 && results?.query !== undefined) {
      insertContainer.innerHTML += `<div class="text-center text-muted">No results found.</div>`
    }

    results.hits.forEach(function(hit) {
      insertContainer.innerHTML += `
            <a class="d-flex p-2 text-decoration-none link text-dark user-block rounded" href="${userUrl.replace(123456789, hit.username)}">
              <div class="col-1 me-3">
                  <img class="img-fluid rounded-circle" src="https://upload.wikimedia.org/wikipedia/commons/e/e6/1kb.png" alt="user-profile-image" id="${hit.username}_image">
              </div>
              <div class="col-11 d-flex align-items-center justify-content-between">
                  <div><span class="fw-bold">${hit.username}</span><br/><span class="text-muted">${hit.name}</span></div>
              </div>
            </a>`;
      preLoadImage(hit.image_url, `${hit.username}_image`)
    })

  }
);


search.addWidgets([
  instantsearch.widgets.searchBox({
    container: '#searchbox',
    placeholder: "Search for users",
    showReset: false,
    showSubmit: false,
    cssClasses: {
      input: ['search-input', 'rounded', 'w-100', 'px-3', 'py-2', 'border-0', 'mb-3']
    }
  }),

  infiniteHits({
    container: document.querySelector('#hits'),
    templates: {
      item: `
            <a class="d-flex p-2 text-decoration-none link text-dark user-block rounded">
              <div class="col-1 me-3">
                  <img class="img-fluid rounded-circle" src="https://upload.wikimedia.org/wikipedia/commons/e/e6/1kb.png" alt="user-profile-image" id="{{ username }}_image">
              </div>
              <div class="col-11 d-flex align-items-center justify-content-between">
                  <div><span class="fw-bold">{{ username }}</span><br/><span class="text-muted">{{ name }}</span></div>
              </div>
            </a>
        `,
      empty: `<div>No results</div>`,
    },
  }),
]);

search.start();