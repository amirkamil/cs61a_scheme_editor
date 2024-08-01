; EECS 390 tweaks
(define (<map-one> func lst)
  (if (null? lst)
      '()
      (cons (func (car lst))
            (<map-one> func (cdr lst))
      )
  )
)

(define (map func list1 . rest)
  (if (null? list1)
      '()
      (cons (apply func (<map-one> car (cons list1 rest)))
            (apply map func (<map-one> cdr (cons list1 rest)))
      )
  )
)

; EECS 390 removals
; (define (filter func lst)
;   (cond ((null? lst) nil)
;         ((func (car lst))
;          (cons (car lst)
;                (filter func (cdr lst))
;          ))
;         (else (filter func (cdr lst)))
;   )
; )
;
; (define (reduce func lst)
;   (cond ((null? lst) nil)
;         ((null? (cdr lst)) (car lst))
;         (else
;          (reduce func
;                  (cons (func (car lst) (car (cdr lst)))
;                        (cdr (cdr lst))
;                  )
;          ))
;   )
; )

(define (cdr-stream stream)
  (force (cdr stream)))

; EECS 390 additions

; syntax
(define-macro (let* vars body-first . body-rest)
    (if (null? vars)
        `(begin ,body-first ,@body-rest)
        `(let ((,(caar vars) ,(cadar vars)))
              (let* ,(cdr vars) ,body-first ,@body-rest)
        )
    )
)

(define-macro (<case-impl> key-evaluated first-branch . rest-branches)
    (cond ((or (eq? (car first-branch) 'else)
               (memv key-evaluated (car first-branch))
           )
           `(begin ,@(cdr first-branch)))
          ((not (null? rest-branches)) `(<case-impl> ,key-evaluated ,@rest-branches))
    )
)
(define-macro (case key first-branch . rest-branches)
    `(<case-impl> ,(eval key) ,first-branch ,@rest-branches)
)
