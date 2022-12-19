import {
  RestEndpointMethodTypes
} from '@octokit/plugin-rest-endpoint-methods/dist-types/generated/parameters-and-response-types'

export interface Options {
  token: string
  owner: string
  repo: string
}

export enum Labels {
  UserStory = 'user-story',
  Deliverable = 'deliverable',
  Subset = 'subset',
  PLD = 'pld',
}

export type Issue = RestEndpointMethodTypes["issues"]["listForRepo"]["response"]["data"][0]
export type CreatedIssue = RestEndpointMethodTypes["issues"]["create"]["response"]["data"]

export type SubsetTree = {
  [key: string]: Issue
} & {
  "0"?: Issue
}

export type DeliverableTree = {
  [key: string]: SubsetTree
} & {
  "0"?: Issue
}

export type PLDTree = {
  [key: string]: DeliverableTree
} & {
  "0"?: Issue
}
