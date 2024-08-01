; EECS 390 additions

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
