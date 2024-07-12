//===================================================================================================================
/* Q.1 In this challenge, the REST API contains information about football matches. The provided API allows querying matches by teams and year. Your task is to get the total number of goals scored by a given team in a given year.
 
To access a collection of matches, perform GET requests to
https://jsonmock.hackerrank.com/api/football_matches?year=<year>&team1=<team>&page=<page>
https://jsonmock.hackerrank.com/api/football_matches?year=<year>&team2=<team>&page=<page>
where <year> is the year of the competition, <team> is the name of the team, and <page> is the page of the results to request. The results might be divided into several pages. Pages are numbered from 1.
 
Notice that the above two URLs are different. The first URL specifies the team1 parameter (denoting the home team) while the second URL specifies the team2 parameter (denoting the visiting team). Thus, in order to get all matches that a particular team played in, you need to retrieve matches where the team was the home team and the visiting team.
 
For example, a GET request to
https://jsonmock.hackerrank.com/api/football_matches?year=2011&team1=Barcelona&page=2
returns data associated with matches in the year 2011, where team1 (the home team) was Barcelona, on the second page of the results.
 
Similarly, a GET request to
https://jsonmock.hackerrank.com/api/football_matches?year=2011&team2=Barcelona&page=1
returns data associated with matches in the year 2011 where team2 (the visiting team) was Barcelona, on the first page of the results.
 
The response to such a request is a JSON with the following 5 fields:
* page: The current page of the results.
* per_page: The maximum number of matches returned per page.
* total: The total number of matches on all pages of the results.
* total_pages: The total number of pages with results.
* data: An array of objects containing matches information on the requested page.
 
Each match record has several fields, but in this task only the following 4 are relevant:
* team1: a string denoting the name of the first team in the match
* team2: a string denoting the name of the second team in the match
* team1goals: a string denoting the number of goals scored by team1 in the match
* team2goals: a string denoting the number of goals scored by team2 in the match
 
Function Description
Complete the function getTotalGoals in the editor below.
 
getTotalGoals has the following parameters:
    string team: the name of the team
    int year: the year of the competition

 * Function to Implement:
 * 
 * /**
 *  * Calculates the total goals scored by a team in a given year
 *  * @param {string} team - The name of the team
 *  * @param {number} year - The year of the competition
 *  * @return {number} The total number of goals scored by the team in the given year


* Task:
* Implement the getTotalGoals function to return the total number of goals scored by the given team
* in all matches (both as team1 and team2) in the specified year.
*/

async function getTotalGoals(team, year) {
  let totalGoals = 0

  async function getGoalsFromPage(teamParam, page) {
    const url = `https://jsonmock.hackerrank.com/api/football_matches?year=${year}&${teamParam}=${team}&page=${page}`
    const response = await fetch(url)
    const data = await response.json()

    let goals = 0
    for (let match of data.data) {
      goals += parseInt(teamParam === 'team1' ? match.team1goals : match.team2goals)
    }
    return { goals, totalPages: data.total_pages }
  }

  for (let page = 1; ; page++) {
    const { goals, totalPages } = await getGoalsFromPage('team1', page)
    totalGoals += goals
    if (page === totalPages) break
  }

  for (let page = 1; ; page++) {
    const { goals, totalPages } = await getGoalsFromPage('team2', page)
    totalGoals += goals
    if (page === totalPages) break
  }
  return totalGoals
}

async function main() {
  const team = 'Barcelona'
  const year = 2011
  const totalGoals = await getTotalGoals(team, year)
  console.log(`Total goals scored by ${team} in ${year}: ${totalGoals}`)
}

main().catch(console.error) //=================================================================================================================

//===================================================================================================================
/* Q.2 In this challenge, the REST API contains information about football competitions and matches. The provided API allows querying competitions by name and year, and it also allows querying matches by competition and year. The task, for a given competition name and year, is to get the total number of goals scored by the team who won the competition.

To access a competition, perform an HTTP GET request to

https://jsonmock.hackerrank.com/api/football_competitions?name=<name>&year=<year>
where <name> is the name of the competition and <year> is the year of the competition.


For example, a GET request to

https://jsonmock.hackerrank.com/api/football_competitions?name=English Premier League&year=2014
returns data associated with the English Premier League in the year 2014.


The response to such a request is a JSON object that contains the property data, which is an array of competitions. In this case, the array will contain only a single item. The item has the following 5 fields:

    name: a string denoting the name of the competition

    country: a string denoting the name of the country of the competition

    year: an integer denoting the year of the competition

    winner: a string denoting the team that won the competition

    runnerup: a string denoting the team that was the runner-up in the competition



Below is an example of such a JSON object:

{
   "name":"English Premier League",
   "country":"England",
   "year":2014,
   "winner":"Chelsea",
   "runnerup":"Manchester City"
}

 

Next, to access a collection of matches played by a given team in a given competition and year, perform GET requests to

https://jsonmock.hackerrank.com/api/football_matches?competition=<competition>&year=<year>&team1=<team>&page=<page>
https://jsonmock.hackerrank.com/api/football_matches?competition=<competition>&year=<year>&team2=<team>&page=<page>

Here, <competition> is the name of the competition, <year> is the year of the competition, <team> is the name of the team, and <page> is the page of the results to request. The results might be divided into several pages. Pages are numbered from 1.

Notice that the above two URLs are different. The first URL specifies the team1 parameter (denoting the home team) while the second URL specifies the team2 parameter (denoting the visiting team). Thus, in order to get all the matches a particular team played in, you need to retrieve matches where the team was the home team and the visiting team.

For example, a GET request to

https://jsonmock.hackerrank.com/api/football_matches?competition=UEFA%20Champions%20League&year=2011&team1=Barcelona&page=2
returns data associated with matches in the UEFA Champions League in the year 2011, where team1 (the home team) was Barcelona, on the second page of the results.

 
Similarly, a GET request to

https://jsonmock.hackerrank.com/api/football_matches?competition=UEFA%20Champions%20League&year=2011&team2=Barcelona&page=1
returns data associated with matches in the UEFA Champions League in the year 2011, where team2 (the visiting team) was Barcelona, on the first page of the results.


The response to such a request is a JSON with the following 5 fields:

    page: The current page of the results.

    per_page: The maximum number of matches returned per page.

    total: The total number of matches on all pages of the results.

    total_pages: The total number of pages with results.

    data: An array of objects containing matches information on the requested page

 

Each match record has several fields, but in this task only the following 4 are relevant:

    team1: a string denoting the name of the first team in the match

    team2: a string denoting the name of the second team in the match

    team1goals: a string denoting the number of goals scored by team1 in the match

    team2goals: a string denoting the number of goals scored by team2 in the match

 

Function Description
Complete the function getWinnerTotalGoals in the editor below.

getWinnerTotalGoals has the following parameters:

    string competition: the name of the competition

    int year: the year of the competition

 

The function must return an integer denoting the total number of goals scored in all matches in the given competition by the team who won the competition.
*/ async function getWinnerTotalGoals(
  competition,
  year
) {
  // First, get the winner of the competition
  const winnerResponse = await fetch(`https://jsonmock.hackerrank.com/api/football_competitions?name=${encodeURIComponent(competition)}&year=${year}`)
  const winnerData = await winnerResponse.json()
  const winner = winnerData.data[0].winner

  async function getGoalsFromPage(teamParam, page) {
    const response = await fetch(
      `https://jsonmock.hackerrank.com/api/football_matches?competition=${encodeURIComponent(competition)}&year=${year}&${teamParam}=${encodeURIComponent(winner)}&page=${page}`
    )
    const data = await response.json()

    let goals = 0
    for (let match of data.data) {
      goals += parseInt(teamParam === 'team1' ? match.team1goals : match.team2goals)
    }
    return { goals, totalPages: data.total_pages }
  }

  let totalGoals = 0

  // Get goals for winner as team1 (home team)
  for (let page = 1; ; page++) {
    const { goals, totalPages } = await getGoalsFromPage('team1', page)
    totalGoals += goals
    if (page === totalPages) break
  }

  // Get goals for winner as team2 (away team)
  for (let page = 1; ; page++) {
    const { goals, totalPages } = await getGoalsFromPage('team2', page)
    totalGoals += goals
    if (page === totalPages) break
  }

  return totalGoals
}
// Example usage
async function main() {
  const competition = 'UEFA Champions League'
  const year = 2011
  const totalGoals = await getWinnerTotalGoals(competition, year)
  console.log(`Total goals scored by the winner of ${competition} in ${year}: ${totalGoals}`)
}

main().catch(console.error)
