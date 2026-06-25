SELECT
    bs.title,
    bs.author,
    bs.isbn
FROM books_staging bs

LEFT JOIN books b
    ON (
        (
            bs.isbn IS NOT NULL
            AND bs.isbn <> ''
            AND bs.isbn = b.isbn
        )
        OR
        (
            (bs.isbn IS NULL OR bs.isbn = '')
            AND bs.title = b.title
            AND bs.author = b.author
        )
    )

GROUP BY
    bs.title,
    bs.author,
    bs.isbn

HAVING COUNT(b.id) > 1;