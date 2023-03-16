// noinspection HtmlDeprecatedAttribute

import {LocaleDictionary} from './locale'
import {Deliverable, PLDSchema, Status, Subset, UserStory, Versions} from './pld'
import {CreatedIssue, DeliverableTree, Issue, PLDTree, SubsetTree} from './types'
import {JSDOM} from 'jsdom'

function checkIfIssueNumberInBody(issueNumber: number, body?: string): boolean {
  if (body === undefined) {
    return false
  }

  return body.includes(`- [x] #${issueNumber}`)
}


export function bodyFromUserStory(locale: LocaleDictionary, userStory: UserStory): string {
  const statusMapper: Record<Status, string> = {
    'To do': locale.to_do,
    'WIP': locale.wip,
    'Done': locale.done,
    'Abandoned': locale.abandoned,
  }

  return (`<table>
    <tr>
        <td colspan="2" align="center" width="2000x">${userStory.name}</td>
    </tr>
    <tr>
        <td>${locale.as_user}:<br>${userStory.user}</td>
        <td>${locale.user_want}:<br>${userStory.action}</td>
    </tr>
    <tr>
        <td colspan="2">${locale.description}: ${userStory.description}</td>
    </tr>
    <tr>
        <td colspan="2">${locale.definition_of_done}:<br>
            <ul>
                ${userStory.definitions_of_done ? userStory.definitions_of_done.map(definition_of_done => `<li>${definition_of_done}</li>`).join('\n') : '' }
            </ul>
        </td>
    </tr>
    <tr>
        <td colspan="2">${locale.assignation}: ${userStory.assignments ? userStory.assignments.join(", ") : ''}</td>
    </tr>
    <tr>
        <td>${locale.estimated_duration}:</td>
        <td>
            ${userStory.estimated_duration} ${locale.man_days} (${Math.ceil(userStory.estimated_duration * 8)} ${locale.hours})
        </td>
    </tr>
    <tr>
        <td>
            ${locale.status}:
        </td>
        <td>
            ${userStory.status ? statusMapper[userStory.status] : ''}
        </td>
    </tr>
    <tr>
        <td colspan="2">${locale.due_date}: ${userStory.due_date}<br>
    </tr>
    <tr>
        <td colspan="2">${locale.end_date}: ${userStory.end_date}<br>
    </tr>
    ${userStory.comments && userStory.comments.length > 0 ? `
    <tr>
        <td colspan="2">${locale.comments}:${userStory.comments instanceof String ? ` ${userStory.comments}` : ''}<br>
            ${userStory.comments instanceof Array ? `<ul>
                ${userStory.comments.map(comment => `<li>${comment}</li>`).join('\n')}
            </ul>` : '' }
        </td>
    </tr>
    ` : '' }
</table>`)
}

export function userStoryFromBody(locale: LocaleDictionary, object: Issue): UserStory {
  const statusMapper: Record<string, Status> = {
    [locale.to_do]: 'To do',
    [locale.wip]: 'WIP',
    [locale.done]: 'Done',
    [locale.abandoned]: 'Abandoned',
  }

  const regexp = new RegExp(`<table>\\s*<tr>\\s*<td colspan="2" align="center" width="2000x">(?<name>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<td>${locale.as_user}:<br>(?<user>[^<]+)<\\/td>\\s*<td>${locale.user_want}:<br>(?<action>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<td colspan="2">${locale.description}: (?<description>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<td colspan="2">${locale.definition_of_done}:<br>\\s*(?<definition_of_done>.+?)\\s*<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<td colspan="2">${locale.assignation}: (?<assignments>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<td>${locale.estimated_duration}:<\\/td>\\s*<td>\\s*(?<estimated_duration>[+-]?([0-9]*[.])?[0-9]+) ${locale.man_days} \\(.*?\\)\\s*<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<td>\\s*${locale.status}:\\s*<\\/td>\\s*<td>\\s*(?<status>[^<]+?)\\s*<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<td colspan="2">${locale.due_date}: (?<due_date>[^<]+)<br>\\s*<\\/tr>\\s*<tr>\\s*<td colspan="2">${locale.end_date}: (?<end_date>[^<]+)<br>\\s*<\\/tr>\\s*(?:<tr>\\s*<td colspan="2">${locale.comments}:(?:| (?<comments_str>[^<]+))<br>\\s*(?:|(?<comments_list>.+?))\\s*<\\/td>\\s*<\\/tr>\\s*)?<\\/table>`, 's')

  const groups = (object.body ?? '').match(regexp)?.groups

  if (groups === undefined) {
    console.log("\n\n\n")
    console.log("ERROR: Please check that the following github issue is in the correct format: " + object.url.replace("api.github.com/repos", "github.com"))
    console.log("\n\n\n")
    throw new Error("Didn't find any groups for this regex")
  }

  const name = groups?.name ?? ''
  const user = groups?.user ?? ''
  const action = groups?.action ?? ''
  const description = groups?.description ?? ''
  const definition_of_done = groups?.definition_of_done ?? ''
  const definition_of_done_dom = Array.from(new JSDOM(definition_of_done).window.document.querySelector("ul")?.querySelectorAll("li") ?? []).map(elem => elem.textContent ?? '')
  const assignments = (groups?.assignments ?? '').split(', ')
  const estimated_duration = parseFloat(groups?.estimated_duration ?? '')
  const status = statusMapper[groups?.status ?? '']
  const due_date = groups?.due_date ?? ''
  const end_date = groups?.end_date ?? ''
  const comments_str = groups?.comments_str
  const comments_list = groups?.comments_list ?? ''
  const comments_list_dom = Array.from(new JSDOM(comments_list).window.document.querySelector("ul")?.querySelectorAll("li") ?? []).map(elem => elem.textContent ?? '')
  const comments = comments_str ?? comments_list_dom

  return {
    type: "user_story", name, user, action, description, definitions_of_done: definition_of_done_dom,
    assignments, estimated_duration, status, due_date, end_date, comments
  }
}

export function bodyFromSubset(locale: LocaleDictionary, subset: Subset, savedSubset?: Issue & CreatedIssue, userStories?: Array<Issue & CreatedIssue>): string {
  return (subset.description ? `# Description
  
${subset.description}`: '') + (savedSubset !== undefined && userStories !== undefined ? `

# Linked issues
${userStories.map(userStory => `
- [${checkIfIssueNumberInBody(userStory.number, savedSubset.body_text) ? 'x' : ' '}] #${userStory.number}`).join('')}
`: '')
}

export function subsetFromBody(locale: LocaleDictionary, object: SubsetTree): Subset {
  const regexp = /(?:# Description\s*(?<description>.+))?/
  const {"0": subset, ...userStories} = object

  const groups = (subset?.body ?? '').match(regexp)?.groups

  if (groups === undefined) {
    throw new Error("Didn't find any groups for this regex")
  }

  const description = groups?.description

  const mappedUserStories = Object.values(userStories).map((userStory) => userStoryFromBody(locale, userStory))

  return {
    type: 'subset',
    name: subset?.title.substring(subset?.title.indexOf(' ') + 1 ?? 0) ?? '',
    description,
    user_stories: mappedUserStories
  }
}

export function bodyFromDeliverable(locale: LocaleDictionary, deliverable: Deliverable, savedDeliverable?: Issue & CreatedIssue, subsets?: Array<Issue & CreatedIssue>): string {
  return (deliverable.description ? `# Description
  
${deliverable.description}` : '') + (savedDeliverable !== undefined && subsets !== undefined ? `

# Linked issues
${subsets.map(subset => `
- [${checkIfIssueNumberInBody(subset.number, savedDeliverable.body_text) ? 'x' : ' '}] #${subset.number}`).join('')}
` : '')
}

export function deliverableFromBody(locale: LocaleDictionary, object: DeliverableTree): Deliverable {
  const regexp = /(?:# Description\s*(?<description>.+))?/
  const {"0": deliverable, ...subsets} = object

  const groups = (deliverable?.body ?? '').match(regexp)?.groups

  if (groups === undefined) {
    throw new Error("Didn't find any groups for this regex")
  }

  const description = groups?.description

  const mappedSubsets = Object.values(subsets).map((subset) => subsetFromBody(locale, subset))

  return {
    type: 'deliverable',
    name: deliverable?.title.substring(deliverable?.title.indexOf(' ') + 1 ?? 0) ?? '',
    description,
    subsets: mappedSubsets
  }
}

export function bodyFromPLD(locale: LocaleDictionary, pld: PLDSchema, savedPLD?: Issue & CreatedIssue, deliverables?: Array<Issue & CreatedIssue>): string {
  return (`# ${locale.document_description}

<table>
    <tr>
        <th>${locale.title}</th>
        <td>${pld.title}</td>
    </tr>
    <tr>
        <th>${locale.subtitle}</th>
        <td>${pld.subtitle ?? ''}</td>
    </tr>
    <tr>
        <th>${locale.description}</th>
        <td>${pld.description ?? ''}</td>
    </tr>
    <tr>
        <th>${locale.locale}</th>
        <td>${pld.locale}</td>
    </tr>
    <tr>
        <th>${locale.authors}</th>
        <td>${pld.authors ? pld.authors.join(', ') : ''}</td>
    </tr>
    <tr>
        <th>${locale.updated_date}</th>
        <td>${pld.versions ? (pld.versions.at(-1)?.date ?? '') : ''}</td>
    </tr>
    <tr>
        <th>${locale.model_version}</th>
        <td>${pld.versions ? (pld.versions.at(-1)?.version ?? '') : ''}</td>
    </tr>
</table>

# ${locale.revision_table}

<table>
    <thead>
        <tr>
            <th>${locale.date}</th>
            <th>${locale.version}</th>
            <th>${locale.authors}</th>
            <th>${locale.sections}</th>
            <th>${locale.comment}</th>
        </tr>
    </thead>
    <tbody>
        ${pld.versions ? pld.versions.map(version => `<tr>
            <td>${version.date}</td>
            <td>${version.version}</td>
            <td>${version.authors ? version.authors.join(', ') : ''}</td>
            <td>${version.sections}</td>
            <td>${version.comment}</td>
        </tr>`).join('\n') : ''}
    </tbody>
</table>`) + (savedPLD !== undefined && deliverables !== undefined ? `

# Linked issues 
${deliverables.map(deliverable => `
- [${checkIfIssueNumberInBody(deliverable.number, savedPLD.body_text) ? 'x' : ' '}] #${deliverable.number}`).join('')}
` : '')
}

export function pldFromBody(locale: LocaleDictionary, object: PLDTree): PLDSchema {
  const {"0": pld, ...deliverables} = object

  const regexp = new RegExp(`# ${locale.document_description}\\s*<table>\\s*<tr>\\s*<th>${locale.title}<\\/th>\\s*<td>(?<title>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<th>${locale.subtitle}<\\/th>\\s*<td>(?<subtitle>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<th>${locale.description}<\\/th>\\s*<td>(?<description>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<th>${locale.locale}<\\/th>\\s*<td>(?<locale>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<th>${locale.authors}<\\/th>\\s*<td>(?<authors>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<th>${locale.updated_date}<\\/th>\\s*<td>(?<updated_date>[^<]+)<\\/td>\\s*<\\/tr>\\s*<tr>\\s*<th>${locale.model_version}<\\/th>\\s*<td>(?<model_version>[^<]+)<\\/td>\\s*<\\/tr>\\s*<\\/table>\\s*# ${locale.revision_table}\\s*<table>\\s*<thead>\\s*<tr>\\s*<th>${locale.date}<\\/th>\\s*<th>${locale.version}<\\/th>\\s*<th>${locale.authors}<\\/th>\\s*<th>${locale.sections}<\\/th>\\s*<th>${locale.comment}<\\/th>\\s*<\\/tr>\\s*<\\/thead>\\s*(?<versions>.+?)\\s*<\\/table>`, 's')

  const groups = (pld?.body ?? '').match(regexp)?.groups

  if (groups === undefined) {
    throw new Error("Didn't find any groups for this regex")
  }

  const title = groups?.title ?? ''
  const subtitle = groups?.subtitle ?? ''
  const description = groups?.description ?? ''
  const pldLocale = groups?.locale
  const authors = groups?.authors.split(", ")
  const versions = '<table>' + (groups?.versions ?? '') + '</table>'
  const versions_dom: Versions = Array.from(new JSDOM(versions).window.document.querySelector("tbody")?.querySelectorAll("tr") ?? []).map(tr => {
    const [date, version, authors, sections, comment] = Array.from(tr.querySelectorAll("td")).map(elem => elem.textContent ?? '')
    return {
      date, version, authors: authors.split(", "), sections, comment
    }
  })

  const mappedDeliverables = Object.values(deliverables).map((deliverable) => deliverableFromBody(locale, deliverable))

  return {
    authors,
    description,
    locale: pldLocale,
    title,
    subtitle,
    deliverables: mappedDeliverables,
    versions: versions_dom
  }
}
