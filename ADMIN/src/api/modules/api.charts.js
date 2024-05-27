import service from '../server'

export const chartsGroup = (data) => {
    return service.post('/v1/charts/group', data)
} 

export const chartsPerson = (data) => {
    return service.post('/v1/charts/person', data)
} 