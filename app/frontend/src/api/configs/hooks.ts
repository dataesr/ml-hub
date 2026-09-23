import { useQuery } from "@tanstack/react-query"
import { getConfig, listConfigs } from "./api"

export function useListConfigs() {
  return useQuery({
    queryKey: ["configs", "list"],
    queryFn: listConfigs,
    refetchOnWindowFocus: false,
  })
}

export function useGetConfig(name: string | null) {
  return useQuery({
    queryKey: ["configs", "get", name],
    queryFn: () => getConfig(name as string),
    enabled: !!name,
    refetchOnWindowFocus: false,
  })
}