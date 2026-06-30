// ===== Happenings: API layer =====
// Codebase has no React/bundler — this is the vanilla equivalent of a
// useEffect+useQuery hook: fetch -> {data, loading, error} -> render callback.

var HappeningsAPI = (function () {
  function fetchEvents(source) {
    var url = '/api/events' + (source ? ('?source=' + source) : '');
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error('events fetch failed: ' + r.status);
      return r.json();
    });
  }

  function fetchEvent(id) {
    return fetch('/api/events/' + encodeURIComponent(id)).then(function (r) {
      if (!r.ok) throw new Error('event fetch failed: ' + r.status);
      return r.json();
    });
  }

  // useQuery-style: runs fetcher, drives {loading,error,data} into onChange(state)
  function useQuery(fetcher, onChange) {
    onChange({ loading: true, error: null, data: null });
    fetcher()
      .then(function (data) { onChange({ loading: false, error: null, data: data }); })
      .catch(function (err) { onChange({ loading: false, error: err, data: null }); });
  }

  return {
    fetchEvents: fetchEvents,
    fetchEvent: fetchEvent,
    useQuery: useQuery,
  };
})();
