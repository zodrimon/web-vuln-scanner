REFLECTED_XSS_PAYLOADS = [
    "<wvs{marker}>alert(1)</wvs{marker}>",
    '"><wvs{marker}>alert(1)</wvs{marker}>',
    "javascript:alert('wvs{marker}')",
]
