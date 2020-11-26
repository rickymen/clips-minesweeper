(defrule generate-combinations
  (number ?x)
  (cell ?a)
  =>
  (assert (combination ?a ?x)))