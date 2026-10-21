text = 'At dawn, while listening to smooth jazz, Anchor Kamran Khan from Geo News met Jazz executives at Gaddafi Stadium.'

test_spans = [
    (3, 6, 'daw'), # start 3, end 6
    (6, 7, 'n'),   # start 6, end 7
    (48, 59, 'Kamran Khan'),
    (65, 73, 'Geo News'),
    (78, 82, 'Jazz'),
    (97, 112, 'Gaddafi Stadium')
]

for s, e, t in test_spans:
    is_frag = False
    if len(t) <= 1 and t.isalpha():
        is_frag = True
    elif (s > 0 and text[s-1].isalnum() and text[s].isalnum()) or (e < len(text) and text[e-1].isalnum() and text[e].isalnum()):
        is_frag = True
    print(f'Span "{t}" ({s}:{e}): Fragment={is_frag}')
