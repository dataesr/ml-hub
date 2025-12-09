import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { listEvals } from "./api"

export function useListEvals() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["evaluate", "list"],
    queryFn: () => listEvals(),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
