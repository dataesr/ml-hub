import { useQuery } from "@tanstack/react-query"
import { useMemo } from "react"
import { getModel, listModels } from "./api"

export function useGetModel(name: string) {
  const { data, error, isFetching } = useQuery({
    queryKey: ["models", "get", name],
    queryFn: () => getModel(name),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}

export function useListModels() {
  const { data, error, isFetching } = useQuery({
    queryKey: ["models", "list"],
    queryFn: () => listModels(),
    refetchOnWindowFocus: false,
    refetchOnMount: false,
    // staleTime: 5 * 60 * 1000,
  })

  const values = useMemo(() => {
    return { data, isFetching, error }
  }, [data, isFetching, error])

  return values
}
