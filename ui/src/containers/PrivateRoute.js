import React from 'react';
import { useSelector } from 'react-redux';
import { Route } from 'react-router-dom';
import { appNamespaceSelector } from '../ducks/namespaceHelper';

const PrivateRoute = ({ component, ...rest }) => {
  const authenticated = useSelector(
    state => !!appNamespaceSelector(state).oidc.user,
  );
  const userManager = useSelector(
    state => appNamespaceSelector(state).config.userManager,
  );

  if (!authenticated) {
    userManager.signinRedirect({
      data: { path: window.location.pathname },
    }); //Go to Dex Login Form if not authenticated
    return null;
  } else {
    const { path } = rest;
    console.log('PrivateRoute path', path);
    console.log('rest', rest);
    if (path.endsWith('createVolume')) {
      console.log('shoud render');
    }
    return <Route {...rest} component={component} />;
  }
};

export default PrivateRoute;
