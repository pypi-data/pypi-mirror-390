let html = document.documentElement

if (window.frameElement) {
    html.setAttribute('page_type', 'iframe')
}
else {
    html.setAttribute('page_type', 'standalone')
}

html.addEventListener('click', async (event) => {
    event.preventDefault()
    let target = event.target
    let uri = target.href || target.src || target.getAttribute('href') || target.getAttribute('src')
    if (uri) {
        window.open(uri, '_blank')
    }
    else if (window.frameElement) {
        window.open(document.URL, '_blank')
    }
})